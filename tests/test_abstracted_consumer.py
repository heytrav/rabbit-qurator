import os
import sys
from unittest import TestCase
from kombu import Connection
from rpc.consumer import RpcConsumer

class TestAbstractMQ(TestCase):

    """Test RabbitMQ interaction"""

    def test_create_rpc(self):
        """Test creating custom rpc endpoint."""

        from rpc import conn_dict
        c = Connection(**conn_dict)
        consumer = RpcConsumer(c)

        @consumer.rpc
        def moffa(msg):
            return {"message": msg}

        self.assertEqual(len(consumer.standard_server_queues), 
                         1, 
                         'One function in queue')

        first_queue = consumer.standard_server_queues[0]
        self.assertEqual(first_queue.name, 'rabbitpy.moffa')
        self.assertEqual(first_queue.routing_key, 'moffa.server')

        @consumer.rpc
        def boffa(msg):
            return {"data": 1}

        self.assertEqual(len(consumer.standard_server_queues), 
                         2, 
                         'Two function in queue')

        second_queue = consumer.standard_server_queues[1]
        self.assertEqual(second_queue.name, 'rabbitpy.boffa')
        self.assertEqual(second_queue.routing_key, 'boffa.server')
        c.release()

        
        
                    

        
