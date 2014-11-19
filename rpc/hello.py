


from kombu import Queue
from kombu.log import get_logger

from rpc import conn_dict
from rpc.exchange import exchange
from rpc.consumer import RpcConsumer

logger = get_logger(__name__)


class Hello(RpcConsumer):

    """Hello service"""

    server_queues = [
        Queue('hello_server_queue', 
            exchange,
            routing_key='hello_server_queue'),
    ]

    def process_rpc(self, body, message):
        """Handle specific message. This version only returns 'Hello, World!'.
        Override this to do other stuff.

        :body: Body of message
        :message: Message object

        """
        logger.info("Processing message: {!r}".format(message.properties))
        logger.info("Request data: {!r}".format(body))
        response = {'message': 'Hello, World!'}
        self.respond_to_client(message, response)


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Hello(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
