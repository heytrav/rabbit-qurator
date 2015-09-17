from unittest import TestCase

from kombu import Connection, Exchange, Queue, Consumer

from ..settings import CONN_DICT


class TestRabbitpy(TestCase):

    """Superclass for qurator testing stuff"""

    exchange_name = 'testqurator'
    conn_dict = CONN_DICT

    def setUp(self):
        """Constructor """
        self._connection = self.connection_factory()
        try:
            self._exchange = Exchange()
        except OSError as derp:
            if isinstance(derp.args[0], ConnectionRefusedError):
                self.skipTest("Not connected to RabbitMQ. Skipping.")
            raise

    def tearDown(self):
        """tear down unit tests """

        for queue in self.queues:
            if not queue.durable:
                queue.purge()
                queue.delete()
        self._connection.release()

    def connection_factory(self):
        """Return connection object
        :returns: Connection object

        """
        print("Connection: {!r}".format(self.conn_dict))
        c = Connection(**self.conn_dict)
        return c

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

    def pull_messages(self,
                      qurator,
                      queues=None,
                      callbacks=None,
                      command=None):
        """Helper to pull messages from a particular queue.

        :qurator: Qurator object
        :command: queue set to pull from
        :callbacks: callbacks from
        """
        if (queues is None or callbacks is None) and command is None:
            raise Exception("Unable to determine "
                            "which queue or callback to use. "
                            "Please provide either both queues and callbacks "
                            "or a command to check")
        if queues is None:
            queues = qurator.queues[command]
        if callbacks is None:
            callbacks = qurator.callbacks[command]
        with Consumer(self._connection, queues, callbacks=callbacks):
            self._connection.drain_events(timeout=1)
