import os
from functools import wraps, partial

from .. import get_logger
from ..settings import LOGGING_CONFIG
logger = get_logger('rabbitpy.utilities', LOGGING_CONFIG)

def preprocess(func=None, *, subset=None):
    """
    Pre process data passed to function to handle jobqueue monstrosity we
    pass around everywhere.

    :func: The name of this function
    :specific_part: string representing "subsection" of this document
    :returns: data to be passed to implemented function.

    """
    if func is None:
        return partial(preprocess, subset=subset)

    @wraps(func)
    def wrapper(legacy_data):
        logger.debug("Calling preprocess with {!r}".format(legacy_data))
        result = {}
        try:
            processed_data = legacy_data['data']['options']
            if subset is not None:
                processed_data = processed_data[subset]
            result = func(processed_data)
            logger.debug("In preprocess function "
                         "returned {!r} ".format(result))
        except KeyError as e:
            logger.error("Caller did not provide proper data structure")
            logger.exception(e)
            raise
        return result
    return wrapper


def postprocess(func=None, *, subset=None):
    """
    Post-process data returned by a function to put stuff in jobqueue
    monstrosity.

    :func: function to wrap
    :returns: processed data structure

    """
    if func is None:
        return partial(postprocess, subset=subset)

    @wraps(func)
    def wrapper(legacy_data):
        """Do whatever function does, but process result back to expected
        :returns: result of function

        """
        logger.debug("Calling postprocess with {!r}".format(legacy_data))
        return_data = {}
        try:
            _ = legacy_data['data']['options']
        except KeyError as ke:
            logger.error("Incorrect data structure"
                         "in postprocess {!r}".format(legacy_data))
            logger.exception(ke)
            raise ke
        try:
            result = func(legacy_data)
            return_data.update(legacy_data)
            logger.debug("In postprocess function returned {!r}".format(result))
            if subset is not None:
                return_data['data']['options'][subset] = result
            else:
                return_data['data']['options'].update(result)
        except Exception as e:
            message = 'Error while executing {!r}: {!r}'.format(func, e)
            logger.exception(message)
            return_data['error'] = message
        logger.debug("Returning from postprocess: {!r}".format(return_data))
        return return_data
    return wrapper
