from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.queues import queues, exchange

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
        return [Consumer(queues=queues,
                         accept=['json', 'pickle'],
                         callbacks=[self.process_task])]


    def process_task(self, body, message):
        """Callback for processing task.

        :body: body of message
        :message: message object

        """
        # Only process if it is an RPC call
        if 'reply_to' in message.properties:
            print("Message: ", message.properties)
            fun = body['fun']
            args = body['args']
            kwargs = body['kwargs']
            logger.info('Got task: %s', reprcall(fun.__name__, args, kwargs))
            try:
                response = fun(*args, **kwdict(kwargs))
            except Exception as exc:
                logger.error('task raised excetion: %r' % exc)
            with Connection(**conn_dict) as conn:
                with producers[conn].acquire(block=True) as producer:
                    logger.info('replying with response %r' % response )
                    send_reply(
                        exchange,
                        message,
                        response,
                        producer
                    )
            message.ack()


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

