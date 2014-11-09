
#from domainsage.search import get_amqp_channel
from domainsage.services import couch_connect
from domainsage.models import Account

#amqp = get_amqp_channel()
couch = couch_connect()

def by_domain(domains=[]):
    """Fetch an account based on domain

    :domains array of domains
    :returns: account info

    """
    result = {}
    query_result = Account.by_domain(couch, domains)
    for row in query_result:
        result[row['key']] = row['value']
    return result
