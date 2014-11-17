import os
import datetime

from unittest import TestCase

from kombu import Connection

class TestKombu(TestCase):

    """Docstring for TestKombu. """

    conn_dict = {
        'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
        'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
        'userid': os.environ['AMQP_USER'],
        'password': os.environ['AMQP_PASSWORD'],
        'ssl': False,
        'virtual_host': os.environ['AMQP_VHOST'],
    }



class SyncTest(TestKombu):

    def test_basic_messaging(self):
        """Test basic producer->consumer behaviour.
        :returns: TODO

        """
        def publisher():
            """Test publisher behaviour
            :returns: TODO

            with Connection(**self.conn_dict) as conn:
                test_queue = conn.SimpleQueue('test_queue')
                message = 'hello world, sent at %s' % datetime.datetime.today()
                test_queue.put(message)
                print('Sent: %s' % message)
                test_queue.close()


        def consumer():
            """Test behaviour of basic amqp consumer

            with Connection(**self.conn_dict) as conn:
                test_queue = conn.SimpleQueue('test_queue')
                message = test_queue.get(block=True, timeout=1)
                print('Received: %s' % message.payload)
                message.ack()
                test_queue.close()
                return message
        publisher()
        message = consumer()
        self.assertRegex(message.payload, r'hello', 'Matches regex')


class AsyncTest(TestKombu):

    def test_async_messaging(self):
        """Test the ConsumerMixin class """
        from kombu import Exchange, Queue, Consumer
        from kombu.log import get_logger
        from kombu.pools import producers
        from kombu.common import send_reply, uuid, collect_replies
        logger = get_logger(__name__)

        test_exchange = Exchange('rabbitpytests', type='direct')
        test_queues = [
            Queue('test1', test_exchange, routing_key='testtask'),
        ]

        # Server side listens for a message and replies to it
        def run_consumer():
            def on_message( body, message):
                print("Called on_message: ", message.properties)
                print("Message channel: ", message.channel.channel_id)
                self.assertRegex(
                    body['data'],
                    r'Hello',
                    'Received "Hello, World" from producer.'
                )
                with Connection(**self.conn_dict) as conn:
                    with producers[conn].acquire(block=True) as producer:
                        send_reply(
                            test_exchange, 
                            message, 
                            {'reply': 'Got it'},
                            producer
                        )
                message.ack()

            with Connection(**self.conn_dict) as conn:
                with Consumer(conn, test_queues, callbacks=[on_message]):
                    conn.drain_events(timeout=3)


        correlation_id = uuid()
        # have producer send a message
        with Connection(**self.conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                payload = {'data': 'Hello, World'}
                producer.publish(payload,
                                 exchange=test_exchange,
                                 serializer='json',
                                 declare=[test_exchange],
                                 routing_key='testtask',
                                 **{
                                     'reply_to': 'testtask',
                                     'correlation_id': correlation_id
                                    })
        run_consumer()
        # check for a reply to the message.
        def on_response(response, message):
            if 'correlation_id' in message.properties: 
                if correlation_id == message.properties['correlation_id']:
                    logger.info("Correlation ids matched")
                    message.ack()

        with Connection(**self.conn_dict) as conn:
            for i in collect_replies(conn, 
                                     conn.channel(),
                                     test_queues[0],
                                     **{'callbacks': [on_response]}
                                     ):
                print("Got reply: ", i)
                self.assertIn('reply', i)
                reply = i['reply']
                self.assertEqual(reply, 'Got it')

