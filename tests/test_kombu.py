from unittest import TestCase
import os

from kombu import Connection
import datetime




class TestKombu(TestCase):

    """Test connection behaviour"""

    conn_dict = {
        'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
        'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
        'userid': os.environ['AMQP_USER'],
        'password': os.environ['AMQP_PASSWORD'],
        'ssl': False,
        'virtual_host': os.environ['AMQP_VHOST'],
    }


    def test_async_messaging(self):
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
