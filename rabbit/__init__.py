# rabbits
import logging
from logging import handlers, Formatter


def get_logger(name=None):
    """Top level logger initialiser thingy.

    :name: str identifying logger
    :returns: logging logger object

    """
    formatter = Formatter(
        '%(pathname)s:line %(lineno)d [%(levelname)s]: %(name)s - %(message)s'
    )
    name_list = ['rabbit']
    if name:
        name_list.append(name)
    logger_name = '.'.join(name_list)
    logger = logging.getLogger(logger_name)
    handler = handlers.SysLogHandler(
        address='/dev/log',
        facility=handlers.SysLogHandler.LOG_DAEMON
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
