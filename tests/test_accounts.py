import unittest

from api.accounts import by_domain

class AccountRabbit(unittest.TestCase):
    """Test access to account info.

        A query result from couchdb looks like this:
            {
                "id":"a004ee19c46ab8cd3bad9d6d16001c20",
                "key":"iwmn-1414347613-1-test.com",
                "value":{
                    "account":"a004ee19c46ab8cd3bad9d6d16001c20",
                    "access":{
                        "status":"registered",
                        "added":1414347613
                        },
                    "name":"test+pythonrabbit@ideegeo.com"
                }
            }
        It needs to get munged into something that looks like this:
        {
            "iwmn-1414347613-1-test.com": {
                "account":"a004ee19c46ab8cd3bad9d6d16001c20",
                "access":{
                    "status":"registered",
                    "added":1414347613
                    },
                "name":"test+pythonrabbit@ideegeo.com"
            },
            "iwmn-1414347613-1-test.com": {
                ...
            }
        }
        ...and later on wrapped in the "msg" datastructure.

        * The core.account.rabbit seems to do each query individually even
        though it should be possible to query as an array?! Not sure if the
        Python implementation is that <metaphor>y.

    """

    def setUp(self):
        """Setup all unit testy stuff
        :returns: TODO
        """
        from domainsage.services import couch_connect
        import time
        c = couch_connect()

        doc = {
            "name": "test+pythonrabbit@ideegeo.com",
            "currency": "USD",
            "domains": {}
        }
        self.domains = []
        for i in range(3):
            d = {}
            now = int(time.time())
            domain = "iwmn-%d-%d-test.com" % (now, i)
            d[domain] = {"status": "registered", "added": now}
            self.domains.append(domain)
            doc["domains"].update(d)

        accounts = c['accounts']
        print("Attempting to save ", doc)
        accounts.save(doc)

        # Message format sent by IWMN callers is something like:
        # msg = {"data":{ "command": "some_command", "options": { "domains": [...]}}}

    def test_account_domain_query(self):
        """Test account query by domain.  """

        result = by_domain(self.domains)
        account = result[self.domains[0]]
        for i in self.domains:
            self.assertIn('account', account, "account key is in.")



