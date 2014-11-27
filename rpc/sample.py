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
def current_time(*args, **kwargs):
    """Return the current time

    :returns: dict with the current time

    """
    return {'time': datetime.datetime.now().isoformat()}

@consumer.rpc(queue_name='rabbitpy.core.domain')
def delegator(body):
    """Implement hase like queue."""

    logger.info("Called method with {!r}".format(body))
    try:
        command = body['command']
        data = body['data']
        if command == 'status_domain':
            return status_domain(data)
        else:
            return {"error": "Unknown command"}
    except KeyError as ke:
        logger.error("'command' key not available {!r}".format(ke))
        return {"error": "Missing 'command' key!"}
    except Exception as e:
        return {"error": "Unable to process request."}

def status_domain(data):
    """Return domain status."""
    return {"available": True, "domain": data['domain']}


if __name__ == '__main__':

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])

        try:
            worker = RpcConsumer(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
