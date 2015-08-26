from unittest.mock import MagicMock, ANY
from kombu import Consumer, Queue
from kombu.utils import nested

from ..queue import Qurator
from ..rpc.client import RpcClient

from .test_rabbit import TestRabbitpy


class TestAbstractMQ(TestRabbitpy):

    """Test RabbitMQ interaction"""

    def setUp(self):
        """Setup unit tests """
        super().setUp()
        self.queues = []

    def pre_declare_queues(self, queues):
        """Pre-declare any queues that will be used in tests.

        :queues: list of names of queues

        """

        declared_queues = []
        for queue_name in queues:
            q = Queue(queue_name,
                      self._exchange,
                      channel=self._connection,
                      durable=self._exchange.durable,
                      routing_key=queue_name)
            q.declare()
            declared_queues.append(q)

        self.queues = declared_queues

    def test_method_wrapping(self):
        """Test creating custom rpc endpoint."""

        self.pre_declare_queues(['qurator.moffa',
                                 'qurator.boffa',
                                 'boffa.moffa'])
        consumer = Qurator(exchange=self._exchange)

        @consumer.rpc
        def moffa(msg):
            pass

        self.assertIn('moffa', consumer.queues)
        moffa_queues = consumer.queues['moffa']
        self.assertEqual(len(moffa_queues),
                         1,
                         'One consumer')
        self.assertEqual(moffa_queues[0].name,
                         'qurator.moffa',
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

        self.pre_declare_queues(['qurator.blah', 'blah.client'])
        consumer = Qurator(exchange=self._exchange)
        checkit = MagicMock(return_value={"msg": "Got reply"})
        # Now mock it!
        consumer.respond_to_client = MagicMock()

        @consumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)

        payload = {"msg": "Hello"}

        # Send message to server
        client = RpcClient(exchange=self._exchange, prefix='qurator')
        reply = client.rpc('blah', payload)

        # Synthetically drain events from queues
        blah_queues = consumer.queues['blah']
        blah_callbacks = consumer.callbacks['blah']
        conn = self._connection
        with Consumer(conn, blah_queues, callbacks=blah_callbacks):
            conn.drain_events(timeout=1)

        checkit.assert_called_with(payload)
        # response = client.retrieve_messages()
        consumer.respond_to_client.assert_called_with(
            ANY,
            {"msg": "Got reply"},
            None
        )

    def test_rpc_client(self):
        """Check behaviour of client """
        self.pre_declare_queues(['qurator.booya'])
        consumer = Qurator(exchange=self._exchange)

        @consumer.rpc
        def booya(*args, **kwargs):
            return {"msg": "Wooot"}

        payload = {"msg": "Boooya"}
        client = RpcClient(exchange=self._exchange, prefix='qurator')
        client.rpc('booya', payload)
        booya_queue = consumer.queues['booya']
        booya_callbacks = consumer.callbacks['booya']

        conn = self._connection
        with Consumer(conn, booya_queue, callbacks=booya_callbacks):
            conn.drain_events(timeout=1)
        reply = client.retrieve_messages()
        self.assertIn('msg', reply)
        self.assertEqual(reply['msg'], 'Wooot')

    def test_default_exchange(self):
        """Test behaviour using the default exchange."""

        from kombu import Exchange
        self._exchange = Exchange(
            channel=self._connection,
            durable=True,
            type='direct')
        self.pre_declare_queues(['qurator.testing_default_exchange'])
        q = Qurator(exchange=self._exchange)

        @q.rpc
        def testing_default_exchange(data):
            return_data = {}
            return_data.update(data)
            return {"x": 1, "data": return_data}

        client = RpcClient(exchange=self._exchange)

        request = {'request': 'my request'}
        client.rpc('testing_default_exchange',
                   request,
                   server_routing_key='qurator.testing_default_exchange')

        queues = q.queues['testing_default_exchange']
        test_callbacks = q.callbacks['testing_default_exchange']
        conn = self._connection
        with Consumer(conn, queues, callbacks=test_callbacks):
            conn.drain_events(timeout=1)
        reply = client.retrieve_messages()
        self.assertIn('x', reply)
        self.assertEqual(reply['data'], request)

    def test_task_nondurable_exchange(self):
        """Task setup """
        from kombu import Exchange
        e = Exchange('', durable=False, type='direct')
        q = Qurator(task_exchange=e, queue='test.nondurable_exchange.queue')

        with self.assertRaises(Exception):
            @q.task
            def amation(data):
                return None

    def test_task_fail(self):
        """What happens when a task fails.
        Expected behaviour is that it does not ack and is left in the queue.
        """
        from kombu import Exchange
        e = Exchange('', type='direct')
        # declare queue
        consumer_queue = Queue('test.task.fail',
                               e,
                               channel=self._connection,
                               routing_key='test.task.fail')
        client_queue = Queue('',
                             e,
                             durable=False,
                             channel=self._connection)
        consumer_queue.declare()
        client_queue.declare()
        self.queues.append(consumer_queue)
        self.queues.append(client_queue)

        q = Qurator(task_exchange=e)

        @q.task(queue_name='test.task.fail')
        def fail(data):
            raise Exception('YOU FAIL!')

        client = RpcClient(exchange=e)
        client.task('fail', {'x': 1}, server_routing_key='test.task.fail')

        curr_queues = q.queues['fail']
        curr_callbacks = q.callbacks['fail']

        def still_around(body, message):
            self.assertFalse(message.acknowledged)
            message.ack()

        curr_callbacks.append(still_around)

        with Consumer(self._connection, curr_queues, callbacks=curr_callbacks):
            self._connection.drain_events(timeout=1)

    def test_task_succeed(self):
        """What happens when a task succeeds.

        Expect it to be acked from the queue.
        """
        from kombu import Exchange
        e = Exchange('', type='direct')
        # declare queue
        consumer_queue = Queue('test.task.succeed',
                               e,
                               channel=self._connection,
                               routing_key='test.task.succeed')
        client_queue = Queue('',
                             e,
                             durable=False,
                             channel=self._connection)
        consumer_queue.declare()
        client_queue.declare()
        self.queues.append(client_queue)

        q = Qurator(task_exchange=e, queue='test.task.succeed')

        @q.task
        def succeed(data):
            return None

        client = RpcClient(exchange=e)
        client.task('succeed',
                    {'x': 1},
                    server_routing_key='test.task.succeed')

        curr_queues = q.queues['succeed']

        @q.rpc
        def still_around(body, message):
            print("Message: {!r}".format(message))

            self._connection.drain_events(timeout=1)
