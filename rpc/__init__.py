import os
import logging
from logging import handlers, Formatter

logging.basicConfig(level=logging.DEBUG)

conn_dict = {
    'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
    'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
    'userid': os.environ['AMQP_USER'],
    'password': os.environ['AMQP_PASS'],
    'ssl': False,
    'virtual_host': os.environ['AMQP_VHOST'],
}


def get_logger(name=None):
    """Top level logger initialiser thingy.

    :name: str identifying logger
    :returns: logging logger object

    """
    formatter = Formatter(
        '%(pathname)s:line %(lineno)d [%(levelname)s]: %(name)s - %(message)s'
    )
    logger = logging.getLogger(name)
    handler = handlers.SysLogHandler(
        address='/dev/log',
        facility=handlers.SysLogHandler.LOG_DAEMON
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
