import logging
import logging.config


def get_logger(name=None):
    """Top level logger initialiser thingy.

    :name: str identifying logger
    :returns: logging logger object

    """
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(name)
    return logger
