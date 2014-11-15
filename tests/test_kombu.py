from unittest import TestCase
import os

from kombu import Connection
import datetime

conn_dict = {
    'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
    'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
    'userid': os.environ['AMQ_USER'],
    'password': os.environ['AMQ_PASSWORD'],
    'ssl': False,
    'virtual_host': os.environ['AMQ_VHOST'],
}



class TestKombu(TestCase):

    """Test connection behaviour"""


    def test_async_messaging(self):
        """Test basic producer->consumer behaviour.
        :returns: TODO

        """
        def publisher():
            """Test publisher behaviour
            :returns: TODO

            """
            with Connection(**conn_dict) as conn:
                simple_queue = conn.SimpleQueue('simple_queue')
                message = 'hello world, sent at %s' % datetime.datetime.today()
                simple_queue.put(message)
                print('Sent: %s' % message)
                simple_queue.close()


        def consumer():
            """Test behaviour of basic amqp consumer

            :stop: fn to stop IO loop during test
            """
            with Connection(**conn_dict) as conn:
                simple_queue = conn.SimpleQueue('simple_queue')
                message = simple_queue.get(block=True, timeout=1)
                print('Received: %s' % message.payload)
                message.ack()
                simple_queue.close()
                return message
        publisher()
        message = consumer()
        self.assertRegex(message.payload, r'hello', 'Matches regex')
