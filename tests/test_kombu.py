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

    conn_dict = {
        'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
        'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
        'userid': os.environ['AMQP_USER'],
        'password': os.environ['AMQP_PASSWORD'],
        'ssl': False,
        'virtual_host': os.environ['AMQP_VHOST'],
    }

    def test_async_messaging(self):
        """Test the ConsumerMixin class """
        from kombu import Exchange, Queue, Consumer
        from kombu.pools import producers

        test_exchange = Exchange('rabbitpytests', type='direct')
        test_queues = [
            Queue('test1', test_exchange, routing_key='testtask'),
        ]

        # Start a consumer and wait
        from threading import Thread
        def run_consumer():
            def on_message( body, message):
                print("Called on_message")
                message.ack()
                print("Consumer got message: %r" % body)
                self.assertRegex(
                    body['data'], 
                    r'Hello', 
                    'Received "Hello, World" from producer.'
                )

            with Connection(**self.conn_dict) as conn:
                with Consumer(conn, test_queues, callbacks=[on_message]):
                    conn.drain_events(timeout=3)

        t = Thread(target=run_consumer)
        t.start()

        # have producer send a message
        with Connection(**self.conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                payload = {'data': 'Hello, World'}
                producer.publish(payload,
                                exchange=test_exchange,
                                 serializer='json',
                                declare=[test_exchange],
                                routing_key='testtask')
