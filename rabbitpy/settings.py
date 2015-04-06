import os
RABBITMQ_SERVICE_HOST=None
RABBITMQ_SERVICE_PORT=None
RABBITMQ_USER=None
RABBITMQ_PASSWORD=None
RABBITMQ_VHOST=None
RABBITMQ_SSL=None
try:
    RABBITMQ_SERVICE_HOST=os.environ['RABBITMQ_SERVICE_HOST']
    RABBITMQ_SERVICE_PORT=os.environ['RABBITMQ_SERVICE_PORT']
    RABBITMQ_USER=os.environ['RABBITMQ_USER']
    RABBITMQ_PASSWORD=os.environ['RABBITMQ_PASSWORD']
    RABBITMQ_VHOST=os.environ['RABBITMQ_VHOST']
    RABBITMQ_SSL=False
except KeyError as ke:
    pass

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "simple":{
            "format": "%(pathname)s:line %(lineno)d [%(levelname)s]: %(name)s - %(message)s"
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
            "handlers": ["consoleHandler"]
        },
        "rabbitpy": {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 1
        },
        "rabbitpy.rpc" : {
            "level": "DEBUG",
            "handlers": ["consoleHandler"],
            "propagate": 1
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

CONN_DICT = {
    'hostname': RABBITMQ_SERVICE_HOST,
    'port': RABBITMQ_SERVICE_PORT,
    'userid': RABBITMQ_USER,
    'password': RABBITMQ_PASSWORD,
    'ssl': RABBITMQ_SSL,
    'virtual_host': RABBITMQ_VHOST,
}
