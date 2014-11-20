from kombu import Queue
from kombu.log import get_logger
from rpc.consumer import RpcConsumer, rpc

logger = get_logger(__name__)

@rpc
class Hello(RpcConsumer):

    """Hello service"""

    def process_rpc(self, body, message):
        """Handle specific message. This version only returns 'Hello, World!'.

        :body: Body of message
        :message: Message object

        """
        response = {'message': 'Hello, World!'}
        self.respond_to_client(message, response)


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    from rpc import conn_dict

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Hello(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
