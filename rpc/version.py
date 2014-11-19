import os
from kombu import Queue
from kombu.log import get_logger

from rpc.exchange import exchange
from rpc.consumer import RpcConsumer

logger = get_logger(__name__)


class Version(RpcConsumer):

    """Version service"""

    server_queues = [
        Queue('rabbitpy.version', 
            exchange,
            routing_key='version.server'),
    ]

        
    def process_rpc(self, body, message):
        """Return the value of the VERSION environment variable

        :body: Body of message
        :message: Message object
        """
        response = {'version': os.environ['VERSION']}
        self.respond_to_client(message, response)


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    from rpc import conn_dict

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Version(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
