from unittest import TestCase

from kombu import Connection,  Exchange

from rpc import conn_dict

class TestRabbitpy(TestCase):

    """Superclass for rabbitpy testing stuff"""

    def setUp(self):
        """Constructor
        :returns: TODO

        """
        self._connection = self.connection_factory()
        self._exchange = Exchange('testrabbitpy',
                                  channel=self._connection,
                                  type='direct',
                                  durable=False)


    def tearDown(self):
        """tear down unit tests """

        [i.purge() for i in self.queues]
        [i.delete() for i in self.queues]
        self._connection.release()


    def connection_factory(self):
        """Return connection object
        :returns: Connection object

        """
        c = Connection(**conn_dict)
        return c


        
