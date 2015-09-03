# main qurator module
#import logging
import logging.config

from .settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
#logger = logging.getLogger(name)
