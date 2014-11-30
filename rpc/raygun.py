import os
import http.client
from kombu.log import get_logger
from raygun4py import raygunprovider

from rpc.iwmnconsumer import IwmnConsumer
from rpc.version import retrieve_version
try:
    import ssl
except ImportError:
    logger.error("No SSL support available.")

logger = get_logger(__name__)

consumer = IwmnConsumer()

def send(msg):
    """Sends request to raygun

    :msg: datastructure
    :returns: http response

    """
    api_key = os.environ['RAYGUN_API_KEY']
    logger.info("Using api key {!r}".format(api_key))
    headers = {
        "X-ApiKey": os.environ['RAYGUN_API_KEY'],
        "Content-Type": 'application/json',
        "User-Agent": "raygun4py"
    }
    conn = http.client.HTTPSConnection('api.raygun.io', 443)
    conn.request('POST', '/entries', msg, headers)
    response = conn.getresponse()
    logger.info("Received: {!r} {!r}".format(response.status,
                                                response.reason))

@consumer.task(queue_name='rabbitpy.raygun')
def send_to_raygun(data):
    """Service endpoint for rabbitpy.raygun.

    :data: request data expected by raygun

    """
    try:
        send(data)
    except Exception  as e:
        logger.error("Exception: {!r}".format(e))
        raise e


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    from rpc import conn_dict
    from rpc.worker import Worker

    setup_logging(loglevel='DEBUG', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Worker(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
