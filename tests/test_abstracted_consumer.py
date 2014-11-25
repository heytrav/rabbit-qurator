import os
import sys
from unittest import TestCase
from unittest.mock import Mock, MagicMock
from kombu import Connection

from rpc import conn_dict
from rpc.consumer import RpcConsumer

class TestAbstractMQ(TestCase):

    """Test RabbitMQ interaction"""

    def connection_factory(self):
        """Return connection object
        :returns: TODO

        """
        c = Connection(**conn_dict)
        return c

    def test_method_wrapping(self):
        """Test creating custom rpc endpoint."""

        conn = self.connection_factory()
        consumer = RpcConsumer(conn)

        @consumer.rpc
        def moffa(msg):
            pass

        self.assertIn('moffa', consumer.consumers)
        moffa_consumers = consumer.consumers['moffa']
        self.assertEqual(len(moffa_consumers),
                         1, 
                         'One consumer')
        self.assertEqual(moffa_consumers[0].queues[0].name,
                         'rabbitpy.moffa',
                         'Queue has expected name')
        @consumer.rpc(queue_name='boffa.moffa')
        def boffa(msg):
            pass


        self.assertIn('boffa', consumer.consumers)
        boffa_consumers = consumer.consumers['boffa']
        boffa_queue = boffa_consumers[0].queues[0]
        self.assertEqual(boffa_queue.name,
                         'boffa.moffa',
                         'Can specify queue name')
        conn.release()


    def test_standard_rpc(self):
        """Check behaviour of wrapped function."""

        conn = self.connection_factory()
        consumer = RpcConsumer(conn)


        checkit = MagicMock(return_value={"msg": "Got reply"})
        @consumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)
        conn.release()

            

        

