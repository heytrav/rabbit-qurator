import types
from functools import wraps
from kombu import Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.exchange import exchange

logger = get_logger(__name__)

class RpcConsumer(ConsumerMixin):

    """Manage server side of RPC connection.

    This code is based on the examples on the Kombu website.
    """
    server_queues = []

    def __init__(self, connection, callbacks=[], server_queues=[]):
        """RpcConsumer(connection)

        :connection: Connection object
        """
        logger.debug("Called constructor.")
        ConsumerMixin.__init__(self)
        self.connection = connection
        # override and add more callbacks to do other processing stuff.
        self.callbacks = [self.ack_message] + callbacks
        if len(server_queues):
            self.server_queues = server_queues


    def get_consumers(self, Consumer, channel):
        """Get a set of consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects

        """
        return RpcConsumer.consumers
        return [Consumer(queues=RpcConsumer.server_queues,
                         accept=['json'],
                         callbacks=self.callbacks)]


    def ack_message(self, body, message):
        """Callback for processing task.

        :body: body of message
        :message: Message object
        """
        try:
            message.ack()
        except Exception as e:
            logger.error('Unable to acknowledge AMQP message: {!r}'.format(e))


    def process_rpc(self, body, message):
        """TODO: Docstring for process_rpc.

        :body: TODO
        :messae: TODO
        :returns: TODO

        """
        pass


    def respond_to_client(self, message, response={}):
        """Send RPC response back to client.

        :response: datastructure that needs to go back to client.
        """
        with Connection(**conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                # Assume reply_to and correlation_id in message.
                try:
                    send_reply(
                        exchange,
                        message,
                        response,
                        producer
                    )
                except KeyError as e:
                    logger.error('Missing key in request {!r}'.format(e))
                except Exception as ex:
                    logger.error('Unable to reply to request {!r}'.format(ex))
                else:
                    logger.info('Replied with response {!r}'.format(response))


def rpc_call():
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        queue_name = '.'.join(['rabbitpy', name])
        queue_route = '.'.join([name, 'server'])
        server_queue = Queue(queue_name, 
                             exchange, 
                             routing_key=queue_route)
        consumer = Consmer(queues=[server_queue], 
                           accept=['json'],
                           callbacks=[func])

        RpcConsumer.consumers.append(consumer)

class RpcCall:
    def __init__(self, func):
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.__wrapped__(*args, **kwargs)


    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)
        
