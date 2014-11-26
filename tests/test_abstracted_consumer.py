import os
import sys
from unittest import TestCase
from unittest.mock import Mock, MagicMock, ANY
from kombu import Connection, Consumer
from kombu.utils import nested

from rpc import conn_dict
from rpc.consumer import RpcConsumer
from rpc.client import RpcClient

class TestAbstractMQ(TestCase):

    """Test RabbitMQ interaction"""

    def connection_factory(self):
        """Return connection object
        :returns: Connection object

        """
        c = Connection(**conn_dict)
        return c

    def test_method_wrapping(self):
        """Test creating custom rpc endpoint."""

        RpcConsumer.standard_server_queues = {}
        RpcConsumer.standard_callbacks = {}
        conn = self.connection_factory()
        consumer = RpcConsumer(conn)

        @RpcConsumer.rpc
        def moffa(msg):
            pass

        self.assertIn('moffa', consumer.standard_server_queues)
        moffa_queues = consumer.standard_server_queues['moffa']
        self.assertEqual(len(moffa_queues),
                         1,
                         'One consumer')
        self.assertEqual(moffa_queues[0].name,
                         'rabbitpy.moffa',
                         'Queue has expected name')
        @RpcConsumer.rpc(queue_name='boffa.moffa')
        def boffa(msg):
            pass


        self.assertIn('boffa', consumer.standard_server_queues)
        boffa_queues = consumer.standard_server_queues['boffa']
        boffa_queue = boffa_queues[0]
        self.assertEqual(boffa_queue.name,
                         'boffa.moffa',
                         'Can specify queue name')
        conn.release()


    def test_standard_rpc(self):
        """Check behaviour of wrapped function."""
        RpcConsumer.standard_server_queues = {}
        RpcConsumer.standard_callbacks = {}

        conn = self.connection_factory()
        consumer = RpcConsumer(conn)


        checkit = MagicMock(return_value={"msg": "Got reply"})
        # Temporarily store the respond_to_client function.
        respond_to_client = RpcConsumer.respond_to_client
        # Now mock it!
        RpcConsumer.respond_to_client = MagicMock()
        @RpcConsumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)


        payload = {"msg": "Hello"}

        # Send message to server
        client = RpcClient()
        corr_id = client.rpc('blah', payload)

        # Synthetically drain events from queues
        blah_queues = RpcConsumer.standard_server_queues['blah']
        blah_callbacks = RpcConsumer.standard_callbacks['blah']
        with Consumer(conn, blah_queues, callbacks=blah_callbacks):
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
        # Unmock the respond_to_client function
        RpcConsumer.respond_to_client = respond_to_client


    def test_rpc_client(self):
        """Check behaviour of client """
        conn = self.connection_factory()
        consumer = RpcConsumer(conn)

        @RpcConsumer.rpc
        def booya(*args, **kwargs):
            return {"msg": "Wooot"}

        payload = {"msg": "Boooya"}
        client = RpcClient()
        corr_id = client.rpc('booya', payload)
        booya_queue = RpcConsumer.standard_server_queues['booya']
        booya_callbacks = RpcConsumer.standard_callbacks['booya']

        with Consumer(conn, booya_queue, callbacks=booya_callbacks):
            conn.drain_events(timeout=1)
        conn.release()
        reply = client.retrieve_messages()
        self.assertIn('msg', reply[0])
        self.assertEqual(reply[0]['msg'], 'Wooot')
