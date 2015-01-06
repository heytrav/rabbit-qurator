# service

import logging
from logging import handlers, Formatter

logging.basicConfig(level=logging.DEBUG)


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
