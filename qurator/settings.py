import os
import sys

DEPLOY_ENVIRONMENT = os.environ.get('DEPLOY_ENVIRONMENT', 'development')
if DEPLOY_ENVIRONMENT is None:
    raise Exception("Please define the local DEPLOY_ENVIRONMENT.")
RABBITMQ_TRANSPORT_SERVICE_HOST = os.environ.get(
    'RABBITMQ_TRANSPORT_SERVICE_HOST',
    'localhost')
RABBITMQ_TRANSPORT_SERVICE_PORT = os.environ.get(
    'RABBITMQ_TRANSPORT_SERVICE_PORT',
    5672)
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST', '/')
RABBITMQ_SSL = os.environ.get('RABBITMQ_SSL', False)

for mq_key in [RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_VHOST]:
    if mq_key is None:
        raise Exception('Must define RABBITMQ_USER, RABBITMQ_PASSWORD and '
                        'RABBITMQ_VHOST.')

CONN_DICT = {
    'hostname': RABBITMQ_TRANSPORT_SERVICE_HOST,
    'port': RABBITMQ_TRANSPORT_SERVICE_PORT,
    'userid': RABBITMQ_USER,
    'password': RABBITMQ_PASSWORD,
    'ssl': RABBITMQ_SSL,
    'virtual_host': RABBITMQ_VHOST,
    'heartbeat': 2
}
