import logging

from kombu import Exchange

from rabbit.queuerate import Queuerator

from domainsage.models import User
from domainsage.services import couch_connect

logger = logging.getLogger(__name__)

default_exchange = Exchange('amq.direct', type='direct')
consumer = Queuerator(queue='api.auth', exchange=default_exchange)

couchdb = couch_connect('development')


@consumer.rpc
def verify_password(data):
    """
    Check a user's password and return whether the password is
    correct.
    """
    try:
        u = User.by_email(couchdb, data.get('user'))
    except Exception:
        return {'verified': False}

    try:
        if u.verify_password(data.get('password')) and u.active:
            return {'verified': True}
    except Exception:
        logger.error('problem hashing and verifying password')
    return {'verified': False}


if __name__ == '__main__':
    consumer.run()
