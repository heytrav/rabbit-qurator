import unittest

from domainsage.services import couch_connect
from rabbitpy.queuerate import Queuerator
from rabbitpy.service.account import accounts_for_domains

from rabbitpy.rpc.client import RpcClient
from tests.test_rabbit import TestRabbitpy

try:
    couchdb = couch_connect()
except Exception as e:
    couchdb = None


@unittest.skipIf(couchdb is None, 'Cannot test without a connection to couch')
class TestAccountService(TestRabbitpy):

    """Tests for account service."""

    def setUp(self):
        """Set up unit test stuff."""
        TestRabbitpy.setUp(self)

    def test_query_with_domain(self):
        """Query the accounts db with a known domain."""

        q = Queuerator(exchange=self._exchange,
                       queue='rabbitpy.test.account')
        self.pre_declare_queues(['rabbitpy.test.account',
                                 'search_domains.client'])

        @q.rpc(queue_name='rabbitpy.test.account')
        def search_domains(data):
            return accounts_for_domains(data['domains'])

        client = RpcClient(exchange=self._exchange)
        client.rpc('search_domains',
                   {"domains": ['iwantmyname.co.nz']},
                   server_routing_key='rabbitpy.test.account')

        self.pull_messages(q, command='search_domains')
        for reply in client.retrieve_messages():
            self.assertIn('iwantmyname.co.nz', reply)
            account = reply['iwantmyname.co.nz']
            self.assertIn('account_handle', account)
            domains = account['domains']
            self.assertIn('iwantmyname.co.nz', domains)
