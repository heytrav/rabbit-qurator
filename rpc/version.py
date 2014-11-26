from kombu import Connection
from kombu.utils.debug import setup_logging
from kombu.log import get_logger

from rpc import conn_dict
from rpc.consumer import RpcConsumer

logger = get_logger(__name__)


consumer = RpcConsumer(Connection(**conn_dict))

@consumer.rpc
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    with open('/etc/d8o/rabbitpy/VERSION') as f:
        version = f.read()
    return {'version': version.strip()}


if __name__ == '__main__':

    setup_logging(loglevel='DEBUG', loggers=[''])
    try:
        consumer.run()
    except KeyboardInterrupt:
        print('bye bye')
