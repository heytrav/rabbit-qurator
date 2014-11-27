from functools import wraps, partial

from kombu import Queue, Connection
from kombu.pools import producers
from kombu.log import get_logger
from kombu.common import send_reply

from rpc import conn_dict
from rpc.exchange import exchange as default_exchange

logger = get_logger(__name__)

class IwmnConsumer(object):

    """Manage Queue and callbacks for a set of Consumers"""

    queues = {}
    callbacks = {}

    def __init__(self, queue_stem='rabbitpy'):
        """Constructor

        :queue_stem: TODO
        :returns: TODO

        """
        self._queue_stem = queue_stem

    def _setup_queue(self, func, callback, exchange, queue_name):
        """TODO: Docstring for _setup_queue.

        :func: TODO
        :exchange: TODO
        :queue_name: TODO
        :returns: TODO

        """
        name = func.__name__.lower()
        if name not in self.queues:
            self.queues[name] = []
        if name not in self.callbacks:
            self.callbacks[name] = []
        if queue_name is None:
            queue_name = '.'.join([self._queue_stem, name])
            routing_key = '.'.join([name, 'server'])
        else:
            routing_key = queue_name
        queue = Queue(queue_name,
                      exchange,
                      durable=False,
                      routing_key=routing_key)


        self.queues[name].append(queue)
        # The callback returned by this decorator doesn't really do anything. The process_msg
        # function added to the consumer is what actually responds to messages
        # from the client on this particular queue.

        self.callbacks[name].append(callback)
        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                pass
            return wrapper
        return decorate


    def task(self, func=None, *, exchange=default_exchange, queue_name=None):
        """Wrap around a function that should be a task.
        The client should not expect anything to be returned.

        """
        if func is None:
            return partial(self.rpc, queue_name=queue_name)

        def process_message(body, message):
            logger.info("Processing function {!r} with data {!r}".format(func.__name__,
                                                                         body))
            response = func(body)
            message.ack()

        return self._setup_queue(func, process_message, exchange, queue_name)



    def rpc(self, func=None, *, exchange=default_exchange, queue_name=None):
        """Wrap around function. This method is modelled after standard RPC
        behaviour where the message sends a reply_to queue and a
        correlation_id back to the client.

        :func: wrap with new standard rpc behaviour
        :exchange: Exchange object.
        :queue_name: defaults to "rabbitpy.<func.__name__>"

        """
        if func is None:
            return partial(self.rpc, queue_name=queue_name)
        def process_message(body, message):
            logger.info("Processing function {!r} with data {!r}".format(func.__name__,
                                                                         body))
            response = func(body)
            message.ack()
            self.respond_to_client(message, response, exchange)

        return self._setup_queue(func,process_message, exchange, queue_name)



    def respond_to_client(self, message, response={}, exchange=default_exchange):
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
                    logger.info('Reself.connectionplied with response {!r}'.format(response))
