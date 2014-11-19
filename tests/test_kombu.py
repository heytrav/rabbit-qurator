import os
import datetime

from unittest import TestCase

from kombu import Connection, Queue, Exchange, Consumer
from kombu.common import send_reply, uuid, collect_replies
from kombu.pools import producers

class TestKombu(TestCase):

    """Test Kombu interaction."""

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


class TestRPC(TestKombu):

    def test_rpc_messaging(self):
        """Test basic RPC interaction."""
        from kombu.log import get_logger
        from rpc.client import check_correlation_id
        logger = get_logger(__name__)

        test_exchange = Exchange('rabbitpytests', type='direct')
        test_queues = [
            Queue('server_queue', test_exchange, routing_key='testtask'),
            Queue('client_queue', test_exchange, routing_key='clienttask')
        ]

        # Server side listens for a message and replies to it
        def run_consumer():
            def on_message( body, message):
                logger.info("Called on_message: %r" % message.properties)
                logger.info("Message channel: %s" % message.channel.channel_id)
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
                                     'reply_to': 'clienttask',
                                     'correlation_id': correlation_id
                                    })
        run_consumer()

        # check for a reply to the message.
        with Connection(**self.conn_dict) as conn:
            for i in collect_replies(conn,
                                     conn.channel(),
                                     test_queues[1],
                                     callbacks=[check_correlation_id]):
                print("Got reply: ", i)
                self.assertIn('reply', i)
                reply = i['reply']
                self.assertEqual(reply, 'Got it')
