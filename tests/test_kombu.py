import os
import datetime

from unittest import TestCase

from kombu import Connection, Queue, Exchange, Consumer
from kombu.common import send_reply, uuid, collect_replies
from kombu.pools import producers

from rpc import conn_dict as connection_data

class TestKombu(TestCase):

    """Test Kombu interaction."""

    conn_dict = connection_data


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

    def test_fetch_reply(self):
        """Test basic RPC interaction."""
        from kombu.log import get_logger
        from rpc.client import FetchReply, send_command
        logger = get_logger(__name__)

        test_exchange = Exchange('rabbitpyrpctests', durable=False, type='direct')
        server_queue = Queue('server_rpc_queue',
                             test_exchange,
                             durable=False,
                             routing_key='test_rpc_task')
        client_queue = Queue('client_rpc_queue',
                             test_exchange,
                             durable=False,
                             routing_key='client_rpc_task')

        # Server side listens for a message and replies to it
        def run_consumer():
            def on_message( body, message):
                logger.info("Received: {!r}".format(body))
                self.assertRegex(
                    body['data']['message'],
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
                with Consumer(conn, [server_queue, client_queue], callbacks=[on_message]):
                    conn.drain_events(timeout=3)


        payload = {'message': 'Hello, World'}
        correlation_id = send_command('hello',
                                      payload,
                                      'test_rpc_task',
                                      client_queue=client_queue,
                                      exchange=test_exchange)
        #correlation_id = uuid()
        ## have producer send a message
        #with Connection(**self.conn_dict) as conn:
        #with producers[conn].acquire(block=True) as producer:
        #payload = {'data': 'Hello, World'}
        #producer.publish(payload,
        #exchange=test_exchange,
        #serializer='json',
        #declare=[test_exchange],
        #routing_key='testtask',
        #**{
        #'reply_to': 'clienttask',
        #'correlation_id': correlation_id
        #})
        run_consumer()
        f = FetchReply()
        response = f.fetch(correlation_id, client_queue)
        self.assertIn('reply', response)
        reply = response['reply']
        self.assertEqual(reply, 'Got it')
