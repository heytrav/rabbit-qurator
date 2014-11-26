import datetime
from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu.log import get_logger

from rpc import conn_dict
from rpc.consumer import RpcConsumer

logger = get_logger(__name__)

@RpcConsumer.rpc
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    with open('/etc/d8o/rabbitpy/VERSION') as f:
        version = f.read()
    return {'version': version.strip()}

@RpcConsumer.rpc
def current_time(*args, **kwargs):
    """Return the current time

    :returns: dict with the current time

    """
    return {'time': datetime.datetime.now().isoformat()}

@RpcConsumer.rpc(queue_name='hello.world')
def say_hello(*args, **kwargs):
    """Just say hi

    :returns: dict with hello

    """
    return {'msg': 'Hello, World!'}


if __name__ == '__main__':

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])

        try:
            consumer = RpcConsumer(conn)
            consumer.run()
        except KeyboardInterrupt:
            print('bye bye')
