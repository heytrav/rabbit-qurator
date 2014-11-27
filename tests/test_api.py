# test code here
import os
from unittest import TestCase

from kombu import Queue, Connection

from rpc import conn_dict



class TestApi(TestCase):

    """Test api code"""

    def setUp(self):
        """Setup unit test
        :returns: TODO

        """
        pass

    def test_queue_decoration(self):
        """Test that decorator creates queues correctly
        :returns: TODO

        """
        from rpc.consumer import Worker, rpc

        @rpc
        class TestConsumer(Worker):
            pass


        c = TestConsumer(Connection(**conn_dict))
        queues = c.server_queues
        self.assertGreaterEqual(len(queues),
                                1,
                                'Consumer has at least one element')
        self.assertIsInstance(queues[0],
                              Queue,
                              'server queues contains Queue object')

        self.assertEqual(queues[0].name,
                         'rabbitpy.testconsumer',
                         'Expected queue name')
        self.assertEqual(queues[0].routing_key,
                         'testconsumer.server',
                         'Expected routing_key')
