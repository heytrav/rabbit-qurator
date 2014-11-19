


import os
from kombu import Queue
from kombu.log import get_logger

from rpc import conn_dict
from rpc.exchange import exchange
from rpc.consumer import RpcConsumer

logger = get_logger(__name__)


class Version(RpcConsumer):

    """Version service"""

    server_queues = [
        Queue('version_server_queue', 
            exchange,
            routing_key='version_server_queue'),
    ]

        
    def process_rpc(self, body, message):
        """Handle specific message. This version only returns 'Version, World!'.
        Override this to do other stuff.

        :body: Body of message
        :message: Message object

        """
        logger.info("Processing message: {!r}".format(message.properties))
        logger.info("Request data: {!r}".format(body))
        response = {'version': os.environ['VERSION']}
        self.respond_to_client(message, response)


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Version(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
