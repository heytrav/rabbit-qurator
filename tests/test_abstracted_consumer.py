import os
import sys
from unittest import TestCase
from unittest.mock import Mock, MagicMock, ANY
from kombu import Connection, Consumer
from kombu.utils import nested

from rpc import conn_dict
from rpc.consumer import RpcConsumer
from rpc.iwmnconsumer import IwmnConsumer
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

        consumer = IwmnConsumer()

        @consumer.rpc
        def moffa(msg):
            pass

        self.assertIn('moffa', consumer.queues)
        moffa_queues = consumer.queues['moffa']
        self.assertEqual(len(moffa_queues),
                         1,
                         'One consumer')
        self.assertEqual(moffa_queues[0].name,
                         'rabbitpy.moffa',
                         'Queue has expected name')
        @consumer.rpc(queue_name='boffa.moffa')
        def boffa(msg):
            pass


        self.assertIn('boffa', consumer.queues)
        boffa_queues = consumer.queues['boffa']
        boffa_queue = boffa_queues[0]
        self.assertEqual(boffa_queue.name,
                         'boffa.moffa',
                         'Can specify queue name')


    def test_standard_rpc(self):
        """Check behaviour of wrapped function."""

        consumer = IwmnConsumer()
        checkit = MagicMock(return_value={"msg": "Got reply"})
        # Now mock it!
        consumer.respond_to_client = MagicMock()
        @consumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)


        payload = {"msg": "Hello"}

        # Send message to server
        client = RpcClient()
        corr_id = client.rpc('blah', payload)

        # Synthetically drain events from queues
        blah_queues = consumer.queues['blah']
        blah_callbacks = consumer.callbacks['blah']
        conn = self.connection_factory()
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


    def test_rpc_client(self):
        """Check behaviour of client """
        consumer = IwmnConsumer()

        @consumer.rpc
        def booya(*args, **kwargs):
            return {"msg": "Wooot"}

        payload = {"msg": "Boooya"}
        client = RpcClient()
        corr_id = client.rpc('booya', payload)
        booya_queue = consumer.queues['booya']
        booya_callbacks = consumer.callbacks['booya']

        conn = self.connection_factory()
        with Consumer(conn, booya_queue, callbacks=booya_callbacks):
            conn.drain_events(timeout=1)
        conn.release()
        reply = client.retrieve_messages()
        self.assertIn('msg', reply[0])
        self.assertEqual(reply[0]['msg'], 'Wooot')
