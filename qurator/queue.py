import os
from uuid import uuid4
import logging
from functools import wraps, partial

from kombu import Queue, Connection, Exchange
from kombu.pools import producers
from kombu.common import send_reply
from amqp import exceptions

from .settings import CONN_DICT

class Qurator(object):

    """Manage Queue and callbacks for a set of Consumers"""

    queues = {}
    callbacks = {}
    dispatch = {}

    def __init__(self,
                 queue=None,
                 prefix='qurator',
                 exchange=Exchange(),
                 task_exchange=Exchange(),
                 conn_dict=CONN_DICT):
        """Constructor

        :prefix: Prefix for consumer queues. Defaults to 'qurator'.
        :queue: Default name for queue
        :exchange: Exchange to use.
        """
        logger = logging.getLogger(__name__)
        self.conn_dict = CONN_DICT
        self._exchange = exchange
        self._task_exchange = task_exchange
        self._prefix = prefix
        self._queue = queue
        logger.debug("Initialised Qurator class")

    def _error(self, error, message):
        """Return an error if caller sent an unknown command.

        :error: Error data
        :message: Message object

        """
        message.ack()
        self.respond_to_client(message, error)

    def _wrap_function(self, function, callback, queue_name, task=False):
        """Set up queue used in decorated function.

        :func: wrapped function
        :exchange: exchange to use
        :queue_name: name of queue
        :returns: wrapped function

        """

        logger = logging.getLogger(__name__)
        name = function.__name__.lower()
        if name not in self.queues:
            self.queues[name] = []
        if name not in self.callbacks:
            self.callbacks[name] = []
        self.callbacks[name].append(callback)
        # If not set by instance, make same as function name.
        if queue_name is None:
            queue_name = '.'.join([self._prefix, name])

        logger.debug("Setting up %s" % queue_name)
        routing_key = queue_name
        # Create the queue.
        exchange = self._exchange

        if task:
            exchange = self._task_exchange
        queue = Queue(queue_name,
                      exchange,
                      durable=exchange.durable,
                      routing_key=routing_key)

        self.queues[name].append(queue)
        # The function returned by the decorator don't really do
        # anything.  The process_msg callback added to the consumer
        # is what actually responds to messages  from the client
        # on this particular queue.

        def decorate(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                pass
            return wrapper
        return decorate

    def task(self, func=None, *, queue_name=None):
        """Wrap around a function that should be a task.
        The client should not expect anything to be returned.

        """
        logger = logging.getLogger(__name__)
        if queue_name:
            logger = logging.getLogger(queue_name)
        if not self._task_exchange.durable:
            raise Exception('Task exchange should be durable.')
        if func is None:
            return partial(self.task, queue_name=queue_name)

        def process_message(body, message):
            logger.debug("Processing function {!r} "
                         " in message: {!r} "
                         "with data {!r}".format(func.__name__,
                                                 message,
                                                 body))
            try:
                func(body)
            except Exception:
                logger.error("Problem processing task", exc_info=True)
            else:
                logger.debug("Ack'ing message.")
                message.ack()

        return self._wrap_function(
            func, process_message, queue_name, task=True)

    def rpc(self, func=None, *, queue_name=None):
        """Wrap around function. This method is modelled after standard RPC
        behaviour where the message sends a reply_to queue and a
        correlation_id back to the client.

        :func: wrap with new standard rpc behaviour
        :queue_name: defaults to "qurator.<func.__name__>"

        """
        if queue_name:
            logger = logging.getLogger(queue_name)
        else:
            logger = logging.getLogger(__name__)
        if func is None:
            return partial(self.rpc, queue_name=queue_name)

        def process_message(body, message):
            logger.debug("Processing function {!r} "
                         "with data {!r}".format(func.__name__, body))
            try:
                properties = message.properties
                correlation_id = properties.setdefault( 'correlation_id', uuid4().hex)
                logger.info('STARTSERVICE:%s;CORRELATION_ID:%s' % (queue_name,
                                                                   correlation_id))
            except Exception:
                logger.error("No correlation id for request!"
                             " {!r}".format(body),
                             exc_info=True)
            response = func(body)
            logger.debug("Wrapped method returned:  {!r}".format(response))
            self.respond_to_client(message, response, queue_name)
            message.ack()

        return self._wrap_function(func, process_message, queue_name)

    def respond_to_client(self, message, response=None, queue_name=None):
        """Send RPC response back to client.

        :response: datastructure that needs to go back to client.
        """
        if response is None:
            response = {}
        if queue_name is None:
            queue_name = __name__
        logger = logging.getLogger(queue_name)
        logger.debug("Replying to queue {!r} with properties: {!r}".format(
            message.properties['reply_to'],
            message.properties['correlation_id']
        ))
        with Connection(**CONN_DICT) as conn:
            with producers[conn].acquire(block=True) as producer:
                try:
                    send_reply(
                        self._exchange,
                        message,
                        response,
                        producer,
                        retry=True,
                        retry_policy={
                            'max_retries': 3,
                            'interval_start': 0,
                            'interval_step': 0.2,
                            'interval_max': 0.2,
                        }
                    )
                except exceptions.AMQPError:
                    logger.error("Problem communicating with rabbit",
                                 exc_info=True)
                except KeyError:
                    logger.error('Missing key in request', exc_info=True)
                except Exception:
                    logger.error('Unable to reply to request', exc_info=True)
                else:
                    correlation_id = message.properties['correlation_id']
                    logger.info('STOPSERVICE:%s;CORRELATION_ID:%s' % (
                        __name__, correlation_id))
                    logger.debug('Replied with response {!r}'.format(response))

    def run(self):
        from .worker import Worker
        logger = logging.getLogger(__name__)
        logger.info("running worker with connection: {!r}".format(self.conn_dict))

        with Connection(**self.conn_dict) as conn:
            try:
                conn.connect()
                worker = Worker(conn, self)
                worker.run()
            except KeyboardInterrupt:
                print('bye bye')
