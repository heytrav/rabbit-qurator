from unittest.mock import MagicMock, ANY
from kombu import Consumer, Queue
from kombu.utils import nested

from rabbit.queuerate import Queuerator
from rpc.client import RpcClient

from tests.test_rabbit import TestRabbitpy


class TestAbstractMQ(TestRabbitpy):

    """Test RabbitMQ interaction"""

    def setUp(self):
        """Setup unit tests """
        TestRabbitpy.setUp(self)
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

        self.pre_declare_queues(['rabbitpy.moffa',
                                 'rabbitpy.boffa',
                                 'boffa.moffa'])
        consumer = Queuerator(legacy=False,
                              exchange=self._exchange)

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

        self.pre_declare_queues(['rabbitpy.blah', 'blah.client'])
        consumer = Queuerator(legacy=False,
                              exchange=self._exchange)
        checkit = MagicMock(return_value={"msg": "Got reply"})
        # Now mock it!
        consumer.respond_to_client = MagicMock()

        @consumer.rpc
        def blah(*args, **kwargs):
            return checkit(*args, **kwargs)

        payload = {"msg": "Hello"}

        # Send message to server
        client = RpcClient(exchange=self._exchange, prefix='rabbitpy')
        client.rpc('blah', payload)

        # Synthetically drain events from queues
        blah_queues = consumer.queues['blah']
        blah_callbacks = consumer.callbacks['blah']
        conn = self._connection
        with Consumer(conn, blah_queues, callbacks=blah_callbacks):
            conn.drain_events(timeout=1)

        checkit.assert_called_with(
            {'data': {'command': 'blah', 'options': payload}}
        )
        # response = client.retrieve_messages()
        consumer.respond_to_client.assert_called_with(
            ANY,
            {"msg": "Got reply"}
        )

    def test_rpc_client(self):
        """Check behaviour of client """
        self.pre_declare_queues(['rabbitpy.booya', 'booya.client'])
        consumer = Queuerator(legacy=False,
                              exchange=self._exchange)

        @consumer.rpc
        def booya(*args, **kwargs):
            return {"msg": "Wooot"}

        payload = {"msg": "Boooya"}
        client = RpcClient(exchange=self._exchange, prefix='rabbitpy')
        client.rpc('booya', payload)
        booya_queue = consumer.queues['booya']
        booya_callbacks = consumer.callbacks['booya']

        conn = self._connection
        with Consumer(conn, booya_queue, callbacks=booya_callbacks):
            conn.drain_events(timeout=1)
        for reply in client.retrieve_messages():
            self.assertIn('msg', reply)
            self.assertEqual(reply['msg'], 'Wooot')

    def test_legacy_rabbit(self):
        """Test creation of legacy style rabbit. """

        self.pre_declare_queues(['testapi.test.queue',
                                 'testlegacy.client',
                                 'yeahimafunction.client'])
        # This shouldn't work.
        with self.assertRaises(Exception):
            consumer = Queuerator()

        # This should.
        legacy_consumer = Queuerator(queue='testapi.test.queue',
                                     exchange=self._exchange)
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

        client = RpcClient(exchange=self._exchange)
        client2 = RpcClient(exchange=self._exchange)

        conn = self._connection
        chan1 = conn.channel()
        chan2 = conn.channel()
        with chan1, chan2:
            consumer1 = Consumer(chan1, queue, callbacks=test_callbacks)
            consumer1.declare()
            consumer2 = Consumer(chan2, queue2, callbacks=test_callbacks2)
            consumer2.declare()
            with nested(consumer1, consumer2):
                client.rpc('testlegacy',
                           data={"x": 1},
                           server_routing_key='testapi.test.queue')

                client2.rpc('yeahimafunction',
                            {"y": 3},
                            server_routing_key='testapi.test.queue')
                # I thought this would actually empty the entire queue, but
                # apparently it doesn't.  Expect two events so drain twice.
                conn.drain_events(timeout=1)
                conn.drain_events(timeout=1)

        check_function.assert_called_with({"x": 1})
        check_another_function.assert_called_with({"y": 3})

        for reply in client.retrieve_messages():
            self.assertIn('result', reply)
            self.assertEqual(reply['result'], 'OK')

        for reply in client2.retrieve_messages():
            self.assertIn('result', reply)
            self.assertEqual(reply['result'], "D'OH")

    def test_malformed_legacy_request(self):
        """Check that we get an error message for a malformed request to the
        legacy queue.

        """
        self.pre_declare_queues(['random.test.queue',
                                 'flappy.client'])
        data_to_send = {"x": "1"}

        server_queue = 'random.test.queue'
        q = Queuerator(queue=server_queue,
                       exchange=self._exchange)

        @q.rpc
        def flappy(data):
            return {"data": "whatever"}

        queues = q.queues['flappy']
        q_callbacks = q.callbacks['flappy']

        # Make client send payload without "command" and "data"
        c = RpcClient(exchange=self._exchange, legacy=False)
        c.rpc('flappy',
              data_to_send,
              server_routing_key=server_queue)
        conn = self._connection
        with Consumer(conn, queues, callbacks=q_callbacks):
            conn.drain_events(timeout=1)
        for reply in c.retrieve_messages():
            self.assertIn('error', reply)
            message = reply['error']
            self.assertRegex(message,
                             r'Malformed request',
                             "Legacy queue requires client with legacy=True.")

    def test_default_exchange(self):
        """Test behaviour using the default exchange."""

        from kombu import Exchange
        self._exchange = Exchange(
            channel=self._connection,
            durable=True,
            type='direct')
        self.pre_declare_queues(['default.queue.thing',
                                 'testing_default_exchange.client'])
        q = Queuerator(exchange=self._exchange,
                       queue='default.queue.thing')

        @q.rpc
        def testing_default_exchange(data):
            return {"x": 1, "data": data}

        client = RpcClient(exchange=self._exchange)

        request = {'request': 'my request'}
        client.rpc('testing_default_exchange',
                   request,
                   server_routing_key='default.queue.thing')

        queues = q.queues['testing_default_exchange']
        test_callbacks = q.callbacks['testing_default_exchange']
        conn = self._connection
        with Consumer(conn, queues, callbacks=test_callbacks):
            conn.drain_events(timeout=1)
        for reply in client.retrieve_messages():
            print("{!r}".format(reply))
            self.assertIn('x', reply)
            self.assertEqual(reply['data'], request)

    def test_task_nondurable_exchange(self):
        """Task setup """
        from kombu import Exchange
        e = Exchange('', durable=False, type='direct')
        q = Queuerator(task_exchange=e, queue='test.nondurable_exchange.queue')

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

        q = Queuerator(task_exchange=e, queue='test.task.fail')

        @q.task
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
        self.queues.append(consumer_queue)
        self.queues.append(client_queue)

        q = Queuerator(task_exchange=e, queue='test.task.succeed')

        @q.task
        def succeed(data):
            return None

        client = RpcClient(exchange=e)
        client.task(
            'succeed', {
                'x': 1}, server_routing_key='test.task.succeed')

        curr_queues = q.queues['succeed']
        curr_callbacks = q.callbacks['succeed']

        def still_around(body, message):
            print("Message: {!r}".format(message))
            self.assertTrue(message.acknowledged)

        curr_callbacks.append(still_around)

        with Consumer(self._connection, curr_queues, callbacks=curr_callbacks):
            self._connection.drain_events(timeout=1)
