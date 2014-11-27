import os
from kombu.log import get_logger
from rpc.worker import Worker, rpc

from raygun4py import raygunprovider

logger = get_logger(__name__)

@rpc
class Raygun(Worker):

    """Raygun service"""

    def process_rpc(self, body, message):
        """Return the current rabbitpy version.

        :body: Body of message
        :message: Message object
        """
        try:
            self.send_to_raygun(body)
        except KeyError as ke:
            logger.error("Missing key: {!r}".format(ke))
        except Exception as e:
            raise e

    def send_to_raygun(self, data):
        """Fire information to raygun.

        :data: request data expected by raygun

        """
        api_key = os.environ['RAYGUN_API_KEY']
        cl = raygunprovider.RaygunSender(api_key)
        cl.set_version(data['version'])
        cl.set_user(data['user'])
        exc_type = data['exc_type']
        exc_value = data['exc_value'],
        exc_traceback = data['exc_traceback']
        request = data['request']
        logger.info("Sending request to raygun {!r}".format(request))
        sent = cl.send(exc_type,
                       exc_value,
                       exc_traceback,
                       data['class'],
                       data['tags'],
                       data['keys'],
                       request)
        logger.debug(sent)
        return sent

if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    from rpc import conn_dict

    setup_logging(loglevel='DEBUG', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Raygun(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
