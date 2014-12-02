import datetime
from kombu.log import get_logger

from rabbit.queuerate import Queuerator

logger = get_logger(__name__)

consumer = Queuerator(queue='rabbitpy.core.domain')

@consumer.rpc
def current_time(*args, **kwargs):
    """Return the current time

    :returns: dict with the current time

    """
    return {'time': datetime.datetime.now().isoformat()}


@consumer.rpc
def status_domain(data):
    """Return domain status."""
    return {
        "available": True, "domain": data['domain']
    }


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    from rpc import conn_dict
    from rabbit.worker import Worker

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])
        try:
            worker = Worker(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
