import os
import sys
from unittest import TestCase
from unittest.mock import Mock, MagicMock, ANY
from kombu import Connection, Consumer
from kombu.utils import nested

from rpc import conn_dict
from rpc.iwmnconsumer import IWMNConsumer
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

        consumer = IWMNConsumer(legacy=False)

        @consumer.rpc
        def moffa(msg):
            pass

        self.assertIn('moffa', consumer.queues)
        moffa_queues = consumer.queues['moffa']
        self.assertEqual(len(moffa_queues),
                         1,
                         'One consumer')
        self.assertEqual(moffa_queues[0].name,
                         'moffa',
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

        consumer = IWMNConsumer(legacy=False)
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
        consumer = IWMNConsumer(legacy=False)

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
        for reply in client.retrieve_messages():
            self.assertIn('msg', reply)
            self.assertEqual(reply['msg'], 'Wooot')


    def test_legacy_rabbit(self):
        """Test creation of legacy style rabbit. """

        # This shouldn't work.
        with self.assertRaises(Exception) as ex:
            consumer = IWMNConsumer()

        # This should.
        legacy_consumer = IWMNConsumer(queue='testapi.test.queue')
        check_function = MagicMock(return_value={"result": "OK"})
        check_another_function = MagicMock(return_value={"result": "D'OH"})

        @legacy_consumer.rpc
        def testlegacy(data):
            return check_function(data)

        @legacy_consumer.rpc
        def yeahimafunction(data):
            return check_another_function(data)

        self.assertIn('testlegacy', legacy_consumer.queues)
        self.assertIn('testlegacy', legacy_consumer.dispatch)
        self.assertIn('yeahimafunction', legacy_consumer.queues)
        self.assertIn('yeahimafunction', legacy_consumer.dispatch)
        queue = legacy_consumer.queues['testlegacy']
        queue2 = legacy_consumer.queues['yeahimafunction']

        test_callbacks = legacy_consumer.callbacks['testlegacy']
        test_callbacks2 = legacy_consumer.callbacks['yeahimafunction']

        client = RpcClient()
        client2 = RpcClient()
        client.rpc('testlegacy', 
                   {"x": 1},
                   server_routing_key='testapi.test.queue')

        client2.rpc('yeahimafunction', 
                    {"y": 3},
                    'testapi.test.queue')

        conn = self.connection_factory()
        chan1 = conn.channel()
        chan2 = conn.channel()
        with chan1, chan2:
            with nested(Consumer(chan1, queue, callbacks=test_callbacks),
                        Consumer(chan2, queue2, callbacks=test_callbacks2)):
                # I thought this would actually empty the queue, but
                # apparently it doesn't.
                # expect two events so drain twice.
                conn.drain_events(timeout=1)
                conn.drain_events(timeout=1)
                
        conn.release()
        check_function.assert_called_with({"x": 1})
        check_another_function.assert_called_with({"y": 3})
        for reply in client.retrieve_messages():
            self.assertIn('result', reply)
            self.assertEqual(reply['result'], 'OK')
        for reply in client2.retrieve_messages():
            self.assertIn('result', reply)
            self.assertEqual(reply['result'], "D'OH")

        
