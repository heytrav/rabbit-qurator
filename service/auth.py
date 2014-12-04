import os
import logging

from rabbit.queuerate import Queuerator

from kombu import Connection, Exchange, Queue, Producer, Consumer

from domainsage.models import User


logger = logging.getLogger(__name__)

default_exchange = Exchange('amq.direct', type='direct')
consumer = Queuerator(queue='api.auth', exchange=default_exchange)

@consumer.rpc
def verify_password(data):
    from domainsage.services import couch_connect
    couchdb = couch_connect('development')
    try:
        u = User.by_email(couchdb, data.get('user'))
    except Exception:
        return { 'verified': False }

    try:
        if u.verify_password(data.get('password')) and u.active:
            return { 'verified': True }
    except Exception:
        logger.error('problem hashing and verifying password')
    return { 'verified': False }

if __name__ == '__main__':
    consumer.run()
