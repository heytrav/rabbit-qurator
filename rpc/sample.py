import datetime
from kombu.log import get_logger

from rpc.queuerate import Queuerator

logger = get_logger(__name__)

consumer = Queuerator()

@consumer.rpc
def current_time(*args, **kwargs):
    """Return the current time

    :returns: dict with the current time

    """
    return {'time': datetime.datetime.now().isoformat()}

@consumer.rpc(queue_name='rabbitpy.core.domain')
def dispatcher(body):
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
        message = "Malformed request {!r}".format(ke)
        logger.error(message)
        return {"error": message}
    except Exception as e:
        message = "Unable to process request: {!r}".format(e)
        logger.error(message)
        return {"error": "Unable to process request."}


def status_domain(data):
    """Return domain status."""
    return {
        "available": True, "domain": data['domain']
    }


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    from rpc import conn_dict
    from rpc.worker import Worker

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])
        try:
            worker = Worker(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
