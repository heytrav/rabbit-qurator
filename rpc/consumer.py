import types
from functools import wraps, partial
from kombu import Queue, Connection, Consumer
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.exchange import exchange as default_exchange

logger = get_logger(__name__)

class RpcConsumer(ConsumerMixin):

    """Manage server side of RPC connection.

    This code is based on the examples on the Kombu website.
    """

    standard_server_queues = []
    standard_callbacks = []
    hase_callbacks = []
    consumers = {}


    def __init__(self, connection):
        """RpcConsumer(connection)

        :connection: Connection object
        """
        logger.debug("Called constructor.")
        ConsumerMixin.__init__(self)
        self.connection = connection


    def get_consumers(self, Consumer, channel):
        """Get a set of consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects

        """
        consumer_set = []
        for i in self.consumers.keys():
            consumer_set += self.consumers[i]

        logger.info("Called get_consumers with {!r}".format(consumer_set))
        return consumer_set


    def rpc(self, func=None, *, exchange=None, queue_name=None):
        """Wrap around function. This method is modelled after standard RPC
        behaviour where the message sends a reply_to queue and a
        correlation_id back to the client.

        :func: wrap with new standard rpc behaviour
        :exchange: Exchange object.
        :queue_name: defaults to "rabbitpy.<func.__name__>"

        """
        if func is None:
            return partial(self.rpc, queue_name=queue_name)

        name = func.__name__.lower()
        if name not in self.consumers:
            self.consumers[name] = []
        if queue_name is None:
            queue_name = '.'.join(['rabbitpy', name])
            routing_key = '.'.join([name, 'server'])
        else:
            routing_key = queue_name
        if exchange is None:
            exchange = default_exchange
        queue = Queue(queue_name,
                      exchange,
                      durable=False,
                      routing_key=routing_key)


        # The callback returned by this decorator doesn't really do anything. The process_msg
        # function added to the consumer is what actually responds to messages
        # from the client on this particular queue.
        def process_msg(body, message):
            logger.info("Processing function {!r} with data {!r}".format(func.__name__,
                                                                         body))
            response = func(body)
            message.ack()
            self.respond_to_client(message, response, exchange)
        c = Consumer(self.connection, queues=[queue], callbacks=[process_msg])
        #c.consume()
        self.consumers[name].append(c)
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                pass
            return wrapper
        return decorate


    def hase(self, name=None):
        """Wrap around function

        :func: TODO
        :returns: TODO

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            #push into consumer callbacks for hase style
            return func(*args, **kwargs)
        return wrapper


    def respond_to_client(self, message, response={}, exchange=default_exchange):
        """Send RPC response back to client.

        :response: datastructure that needs to go back to client.
        """
        with self.connection as conn:
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
