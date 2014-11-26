import os
import sys
from unittest import TestCase
from unittest.mock import Mock, MagicMock, ANY
from kombu import Connection

from rpc import conn_dict
from rpc.consumer import RpcConsumer
from rpc.client import RpcClient

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
        consumer.respond_to_client = MagicMock()
        @consumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)


        payload = {"msg": "Hello"}

        # Send message to server
        client = RpcClient()
        corr_id = client.rpc('blah', payload)

        conn.drain_events(timeout=1)
        checkit.assert_called_with(
            {'command': 'blah', 'data': payload}
        )
        conn.release()
        #response = client.retrieve_messages()
        consumer.respond_to_client.assert_called_with(
            ANY,
            {"msg": "Got reply"},
            ANY
        )

    def test_rpc_client(self):
        """Check behaviour of client
        :returns: TODO

        """
        conn = self.connection_factory()
        consumer = RpcConsumer(conn)

        @consumer.rpc
        def booya(*args, **kwargs):
            return {"msg": "Wooot"}
        
        payload = {"msg": "Boooya"}
        client = RpcClient()
        corr_id = client.rpc('booya', payload)

        conn.drain_events(timeout=1)
        conn.release()
        reply = client.retrieve_messages()
        self.assertIn('msg', reply[0])
        self.assertEqual(reply[0]['msg'], 'Wooot')

        

