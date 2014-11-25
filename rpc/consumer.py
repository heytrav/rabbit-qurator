import types
from functools import wraps, partial
from kombu import Queue, Connection, Consumer
#from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.pools import producers
from kombu.common import send_reply

from rpc import conn_dict
from rpc.exchange import exchange as default_exchange

logger = get_logger(__name__)

class RpcConsumer(object):

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
        #ConsumerMixin.__init__(self)
        self.connection = connection
        # override and add more callbacks to do other processing stuff.
        #self.callbacks = [self.ack_message, self.process_rpc,]


    #def get_consumers(self, Consumer, channel):
        #"""Get a set of consumers.

        #:Consumer: Consumer object
        #:channel: a channel
        #:returns: array of Consumer objects

        #"""
        #return [Consumer(queues=self.standard_server_queues,
                         #accept=['json'],
                         #callbacks=self.standard_callbacks)]


    #def ack_message(self, body, message):
        #"""Callback for processing task.

        #:body: body of message
        #:message: Message object
        #"""
        #try:
            #message.ack()
        #except Exception as e:
            #logger.error('Unable to acknowledge AMQP message: {!r}'.format(e))


    def rpc(self, func=None, *, exchange=default_exchange, queue_name=None):
        """Wrap around function.

        :func: wrap with new standard rpc behaviour

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
        queue = Queue(queue_name,
                      exchange,
                      durable=False,
                      routing_key=routing_key)
        c = Consumer(self.connection)
        c.add_queue(queue)
        self.consumers[name].append(c)
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                def process_msg(body, message):
                    response = func(body)
                    self.respond_to_client(message, response)
                c.register_callback(process_msg)
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



    def process_rpc(self, body, message):
        """Override with whatever functionality is required by rpc or task.

        This is a callback that is passed on to the consumer mixin.

        :body: dict containing data to be processed by rabbit
        :message: object
        """
        response = self.process_rpc_func(body)



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

def rpc(cls):
    """Setup some of the rpc bits

    :cls: Object
    :returns: Same object but with server queues declared.

    """
    name = cls.__name__.lower()
    queue_name = '.'.join(['rabbitpy', name])
    routing_key = '.'.join([name, 'server'])
    cls.server_queues = [Queue(queue_name,
                               exchange,
                               durable=False,
                               routing_key=routing_key)]
    return cls


