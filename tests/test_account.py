import unittest

from domainsage.services import couch_connect
from service.account import account_queuerator

from rpc.client import RpcClient
from rabbit.exchange import exchange
from tests.test_rabbit import TestRabbitpy

try:
    couchdb = couch_connect()
except Exception as e:
    couchdb = None


@unittest.skipIf(couchdb is None, 'Cannot test without a connection to couch')
class TestAccountService(TestRabbitpy):

    """Tests for account service."""

    def test_query_with_domain(self):
        """Query the accounts db with a known domain."""
        self._exchange = exchange
        self.pre_declare_queues(['rabbitpy.core.account'])
        client = RpcClient(exchange=self._exchange)

        client.rpc('account_for_domain',
                   {"domains": ['iwantmyname.co.nz']},
                   server_routing_key='rabbitpy.core.account')
        self.pull_messages(account_queuerator, command='account_for_domain')
        for reply in client.retrieve_messages():
            self.assertIn('iwantmyname.co.nz', reply)
            account = reply['iwantmyname.co.nz']
            self.assertIn('account_handle', account)
            domains = account['domains']
            self.assertIn('iwantmyname.co.nz', domains)
