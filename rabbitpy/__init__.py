# main rabbitpy module
import logging
import logging.config

from rabbitpy.settings import LOGGING_CONFIG


def get_logger(name=None):
    """Top level logger initialiser thingy.

    :name: str identifying logger
    :returns: logging logger object

    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    logger.debug("Just created logger with config {!r}".format(LOGGING_CONFIG))
    return logger
