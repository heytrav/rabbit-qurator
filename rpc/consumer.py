from kombu import Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.queues import client_exchange, consumer_exchange

logger = get_logger(__name__)

class RpcConsumer(ConsumerMixin):

    """Manage server side of RPC connection.

    This code is based on the examples on the Kombu website.
    """
    server_queues = [
        Queue('server_hello', consumer_exchange,
              routing_key='server_hello')
    ]

    def __init__(self, connection):
        """RpcConsumer(connection)

        :connection: Connection object
        """
        ConsumerMixin.__init__(self)
        self.connection = connection
        # override and add more callbacks to do other processing stuff.
        self.callbacks = [self.ack_message, self.process_rpc,]


    def get_consumers(self, Consumer, channel):
        """Get a set of consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects

        """
        return [Consumer(queues=self.server_queues,
                         accept=['json'],
                         callbacks=self.callbacks)]


    def ack_message(self, body, message):
        """Callback for processing task.

        :body: body of message
        :message: message object
        """
        try:
            message.ack()
        except Exception as e:
            logger.error('Unable to acknowledge AMQP message: %r' % e)


    def process_rpc(self, body, message):
        """Handle specific message. This version only returns 'Hello, World!'.
        Override to do other stuff.

        :body: Body of message
        :message: Message object

        """
        # Only process if it is an RPC call. Assume that 'reply_to' in the
        # message properties means that it is RPC.
        if 'reply_to' in message.properties:
            logger.info("Message: %r", message.properties)
            response = {'message': 'Hello, World!'}
            self.respond_to_client(message, response)


    def respond_to_client(self, message, response={}):
        """Send RPC response back to client.

        :response: datastructure that needs to go back to client.
        """
        logger.info('Respond to client: %r' % response)
        with Connection(**conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                logger.info('Replying with response %r' % response )
                send_reply(
                    client_exchange,
                    message,
                    response,
                    producer
                )


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = RpcConsumer(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
