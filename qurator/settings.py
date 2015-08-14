import os
import sys

DEPLOY_ENVIRONMENT = os.environ.get('DEPLOY_ENVIRONMENT', None)
if DEPLOY_ENVIRONMENT is None:
    raise Exception("Please define the local DEPLOY_ENVIRONMENT.")
RABBITMQ_TRANSPORT_SERVICE_HOST = os.environ.get(
    'RABBITMQ_TRANSPORT_SERVICE_HOST',
    'localhost')
RABBITMQ_TRANSPORT_SERVICE_PORT = os.environ.get(
    'RABBITMQ_TRANSPORT_SERVICE_PORT',
    5672)
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
RABBITMQ_VHOST = os.environ.get('RABBITMQ_VHOST')
RABBITMQ_SSL = os.environ.get('RABBITMQ_SSL', False)

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "[%(deploy_environment)s] %(pathname)s:line %(lineno)d [%(levelname)s]: %(name)s - %(message)s"
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 0
        },
        "rabbitpy": {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 0
        },
        "rabbitpy.rpc": {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 0
        },
        "rabbitpy.utilities": {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 0
        }
    }
}

# Copy pasted (with impunity) from domainsage.settings
try:
    if 'RABBITPY_SETTINGS_DIR' in os.environ:
        local_settings_dir = os.path.realpath(
            os.path.expanduser(
                os.environ['RABBITPY_SETTINGS_DIR']))
        sys.path.insert(0, local_settings_dir)
    from local_settings import *
except ImportError:
    pass

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
