import os
from functools import wraps, partial

from . import get_logger
from .settings import LOGGING_CONFIG
logger = get_logger('rabbitpy.utilities', LOGGING_CONFIG)

def jobqueue_preprocess(func=None, specific_part=None):
    """Pre process data passed to function to handle jobqueue monstrosity we
    pass around everywhere.

    :func: The name of this function
    :specific_part: string representing "subsection" of this document
    :returns: data to be passed to implemented function.

    """
    pass

def jobqueue_postprocess(func=None):
    """Post-process data returned by a function to put stuff in jobqueue
    monstrosity.

    :func: function to wrap
    :returns: processed data structure

    """
    pass
