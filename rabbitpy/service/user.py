import logging

from kombu import Exchange

from rabbitpy.queuerate import Queuerator

from domainsage.models import User
from domainsage.services import couch_connect

logger = logging.getLogger(__name__)

default_exchange = Exchange('amq.direct', type='direct')
q = Queuerator(queue='api.user', exchange=default_exchange)

couchdb = couch_connect('development')


@q.rpc
def domains(data):
    """ Return list of domains a user has access to. """
    try:
        domains = []
        u = User.by_email(couchdb, data.get('user'))
    except Exception:
        return {'domains': []}

    for account in u.accounts:
        domains.extend(list(account.domains.keys()))

    return {'response': {'domains': domains}}


if __name__ == '__main__':
    q.run()
