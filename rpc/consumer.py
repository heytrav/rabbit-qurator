from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from .queues import queues

logger = get_logger(__name__)

conn_dict = {
    'hostname': os.environ['AMQ_PORT_5672_TCP_ADDR'],
    'port': os.environ['AMQ_PORT_5672_TCP_PORT'],
    'userid': os.environ['AMQP_USER'],
    'password': os.environ['AMQP_PASSWORD'],
    'ssl': False,
    'virtual_host': os.environ['AMQP_VHOST'],
}

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

        :Consumer: TODO
        :channel: TODO
        :returns: TODO

        """
        return [Consumer(queues=queues,
                         accept=['json'],
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        """TODO: Docstring for process_task.

        :body: body of message
        :message: message object

        """
        fun = body['fun']
        args = body['args']
        kwargs = body['kwargs']
        logger.info('Got task: %s', reprcall(fun.__name__, args, kwargs))
        try:
            fun(*args, **kwdict(kwargs))
        except Exception as exc:
            logger.error('task raised excetion: %r', exc)
        message.ack()

if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    setup_loggin(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')

