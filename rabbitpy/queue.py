import os
from functools import wraps, partial

from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import send_reply
from amqp import exceptions

from . import get_logger
from .settings import CONN_DICT
from .exchange import exchange as default_exchange
from .exchange import task_exchange as default_task_exchange
logger = get_logger(__name__)


class Qurator(object):

    """Manage Queue and callbacks for a set of Consumers"""

    queues = {}
    callbacks = {}
    dispatch = {}

    def __init__(self,
                 legacy=True,
                 queue=None,
                 prefix='rabbitpy',
                 exchange=default_exchange,
                 task_exchange=default_task_exchange):
        """Constructor

        :legacy: Boolean flag. If False (default) it should try to emulate hase
        functionality by dispatching calls to a single queue to different
        functions. If False, assume that each method is its own queue.
        :prefix: Prefix for consumer queues. Defaults to 'rabbitpy'.
        :queue: Default name for queue
        :exchange: Exchange to use.
        """
        self._exchange = exchange
        self._task_exchange = task_exchange
        self._prefix = prefix
        self._legacy = legacy
        if legacy:
            if queue is None:
                raise Exception("'queue' is required "
                                " for legacy implementation.")

        self._queue = queue
        logger.debug("Initialising Qurator class")

    def _error(self, error, message):
        """Return an error if caller sent an unknown command.

        :error: Error data
        :message: Message object

        """
        message.ack()
        self.respond_to_client(message, error)

    def _hase_dispatch(self, body, message):
        """Dispatch function calls to wrapped methods

        :body: data for command. Note: this must contain  a key 'command'
        which dispatch which callback will be called.
        :returns: the data returned by the callback.
        """
        logger = get_logger(self._queue)
        try:
            command = body['data']['command']
            callback = self.dispatch[command]
            logger.debug("Calling {!r} with {!r}".format(command, body))
        except KeyError as ke:
            error_message = "Malformed request: {!r}".format(ke)
            logger.error(error_message)
            error = {"error": error_message, "sent": body}
            self._error(error, message)
        except Exception as e:
            error_message = "Unable call method: {!r}".format(e)
            logger.error(error_message)
            error = {"error": error_message, "sent": body}
            self._error(error, message)
        else:
            return callback(body, message)

    def _wrap_function(self, function, callback, queue_name, task=False):
        """Set up queue used in decorated function.

        :func: wrapped function
        :exchange: exchange to use
        :queue_name: name of queue
        :returns: wrapped function

        """
        name = function.__name__.lower()
        if name not in self.queues:
            self.queues[name] = []
        if name not in self.callbacks:
            self.callbacks[name] = []
        if self._legacy:
            self.dispatch[name] = callback
            # Expect that there will only be one callback with this particular
            # name.
            self.callbacks[name] = [self._hase_dispatch]
            # Set queue_name to whatever class was instantiated with.
            queue_name = self._queue
        else:
            self.callbacks[name].append(callback)

        # If not set by instance, make same as function name.
        if queue_name is None:
            queue_name = '.'.join([self._prefix, name])

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
        logger = get_logger()
        if queue_name:
            logger = get_logger(queue_name)
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
            except Exception as e:
                msg = "Problem processing task: {!r}".format(e)
                logger.error(msg)
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
        :queue_name: defaults to "rabbitpy.<func.__name__>"

        """
        logger = get_logger()
        if queue_name:
            logger = get_logger(queue_name)
        if func is None:
            return partial(self.rpc, queue_name=queue_name)

        def process_message(body, message):
            logger.debug("Processing function {!r} "
                         "with data {!r}".format(func.__name__, body))
            response = func(body)
            logger.debug("Wrapped method returned:  {!r}".format(response))
            self.respond_to_client(message, response)
            message.ack()

        return self._wrap_function(func, process_message, queue_name)

    def respond_to_client(self, message, response={}):
        """Send RPC response back to client.

        :response: datastructure that needs to go back to client.
        """
        logger.debug("Replying to queue {!r} with properties: {!r}".format(
            message.properties['reply_to'],
            message.properties['correlation_id']
        ))
        with Connection(**CONN_DICT) as conn:
            with producers[conn].acquire(block=True) as producer:
                # Assume reply_to and correlation_id in message.

                # Note this also assumes that the client has a bound queue
                # on the same exchange as this worker.
                #
                # This is not the case for hase, since it uses a generated
                # queue name and the default exchange which has an implicit
                # binding from routing_key => queue name
                #
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
                except exceptions.AMQPError as amqp_error:
                    logger.error("Problem communicating "
                                 "with rabbit {!r}".format(amqp_error))
                except KeyError as e:
                    logger.error('Missing key in request {!r}'.format(e))
                except Exception as ex:
                    logger.error('Unable to reply to request {!r}'.format(ex))
                else:
                    logger.info('Replied with response {!r}'.format(response))

    def run(self):
        from kombu import Connection

        from .settings import CONN_DICT
        from .worker import Worker

        with Connection(**CONN_DICT) as conn:
            try:
                worker = Worker(conn, self)
                worker.run()
            except KeyboardInterrupt:
                print('bye bye')
