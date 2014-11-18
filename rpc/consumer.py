import os
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.queues import server_queues, producer_exchange


logger = get_logger(__name__)


class Worker(ConsumerMixin):

    """Manage server side of RPC connection."""

    def __init__(self, connection):
        """Worker(connection)

        :connection: Connection object
        """
        ConsumerMixin.__init__(self)
        self.connection = connection


    def get_consumers(self, Consumer, channel):
        """Get consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects

        """
        return [Consumer(queues=server_queues,
                         accept=['json'],
                         callbacks=[self.process_rpc])]


    def process_rpc(self, body, message):
        """Callback for processing task.

        :body: body of message
        :message: message object

        """
        # Only process if it is an RPC call
        if 'reply_to' in message.properties:
            print("Message: ", message.properties)
            command = body['command']
            data = body['data']
            meta = body['meta']
            message.ack()
            if command == 'version':
                response = {'version': os.environ['VERSION']}
            elif command == 'hello':
                response = {'message': 'Hello, World!'}
            else:
                response = {'status': 'error', 'message': 'Unknown command'}
            with Connection(**conn_dict) as conn:
                with producers[conn].acquire(block=True) as producer:
                    logger.info('replying with response %r' % response )
                    send_reply(
                        producer_exchange,
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
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')

