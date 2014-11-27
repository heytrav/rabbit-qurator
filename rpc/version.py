import datetime
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu.log import get_logger

from rpc import conn_dict
from rpc.consumer import RpcConsumer
from rpc.iwmnconsumer import IwmnConsumer

logger = get_logger(__name__)

consumer = IwmnConsumer()
@consumer.rpc
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    with open('/etc/d8o/rabbitpy/VERSION') as f:
        version = f.read()
    return {'version': version.strip()}

@consumer.rpc
def current_time(*args, **kwargs):
    """Return the current time

    :returns: dict with the current time

    """
    return {'time': datetime.datetime.now().isoformat()}

@consumer.rpc(queue_name='hello.world')
def say_hello(*args, **kwargs):
    """Just say hi

    :returns: dict with hello

    """
    return {'msg': 'Hello, World!'}

@consumer.rpc(queue_name='api.core.domain')
def delegator(body, message):
    """Implement hase like queue

    :*args: TODO
    :**kwargs: TODO
    :returns: TODO

    """
    logger.info("Called method with {!r}".format(body))
    if 'command' in body:
        logger.info("yey")


if __name__ == '__main__':

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])

        try:
            worker = RpcConsumer(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
