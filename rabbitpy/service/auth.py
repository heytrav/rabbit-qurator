import logging

from kombu import Exchange

from rabbit.queuerate import Queuerator

from domainsage.models import User
from domainsage.services import couch_connect

from utils.logging import get_logger
logger = get_logger('auth')

default_exchange = Exchange('amq.direct', type='direct')
q = Queuerator(queue='api.auth', exchange=default_exchange)

couchdb = couch_connect()


@q.rpc
def verify_password(data):
    """
    Check a user's password and return whether the password is
    correct.
    """
    logger.debug("Received: {!r}".format(data))
    try:
        u = User.by_email(couchdb, data.get('user'))
    except Exception as e:
        logger.error("Error querying couch {!r}".format(e))
        return {'verified': False}

    try:
        if u.verify_password(data.get('password')) and u.active:
            return {'verified': True}
    except Exception:
        logger.error('problem hashing and verifying password')
    return {'verified': False}


if __name__ == '__main__':
    q.run()
