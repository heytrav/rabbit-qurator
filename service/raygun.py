import os
import logging
import http.client

from rabbit.queuerate import Queuerator


logger = logging.getLogger(__name__)

consumer = Queuerator(legacy=False)


def send(msg):
    """Sends request to raygun

    :msg: datastructure
    :returns: http response

    """
    api_key = os.environ['RAYGUN_API_KEY']
    logger.info("Using api key {!r}".format(api_key))
    headers = {
        "X-ApiKey": api_key,
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
    except Exception as e:
        logger.error("Exception: {!r}".format(e))
        raise e


if __name__ == '__main__':
    consumer.run()
