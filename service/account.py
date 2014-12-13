import os
import logging
from domainsage.models import Account
from domainsage.services import couch_connect

from rabbit.queuerate import Queuerator

logger = logging.getLogger(__name__)

# TODO configurify the db environment somewheres
couchdb = couch_connect('development')

account_queuerator = Queuerator(queue='rabbitpy.core.account')


@account_queuerator.rpc
def account_for_domain(data):
    """Return account info for a particular domain

    :data: dict Sent by client
    :returns: dict

    """
    logger.debug("Received query: {!r}".format(data))
    domains = data['domains']
    return accounts_for_domains(domains)


def accounts_for_domains(domains):
    """Search for accounts for domains.

    :domains: list of domains to search
    :returns: dict with account for each domain in list

    """
    account_results = Account.for_domains(couchdb, domains)
    for domain in domains:
        acct = account_results[domain]
        account_dict = dict(acct.unwrap().items())
        account_results[domain] = account_dict
    return account_results

if __name__ == '__main__':
    account_queuerator.run()
