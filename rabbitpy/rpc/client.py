from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import uuid, collect_replies
from amqp import exceptions


from .. import get_logger
from ..settings import CONN_DICT
from ..exchange import exchange as default_exchange

logger = get_logger(__name__)


class RpcClient(object):

    """Process a RPC queue and fetch the response."""

    reply_received = False
    messages = {}
    corr_id_server_queue = {}

    def __init__(self,
                 legacy=True,
                 exchange=default_exchange,
                 prefix=None,
                 client_queue=None):
        """Constructor for client object.

        :legacy: Boolean flag for hase-like (default) or standard rpc
        :exchange: Exchange to use
        :prefix: for automatic server routing key generation
        :client_queue: name for the client queue. Default is <command>.client
        """
        self._legacy = legacy
        self._prefix = prefix
        self._exchange = exchange
        self.reply = None
        self._client_queue = client_queue
        self._queue = None
        self._conn = Connection(**CONN_DICT)

    def retrieve_messages(self):
        """Process the message queue and ack the one that matches the
        correlation_id sent to the server.

        :correlation_id: Expected correlation id (uuid).
        :queue: The queue to read.
        :returns: JSON object retrieved from the queue.

        """

        logger.debug("Client queue: {!r}".format(self._client_queue))
        client_queue = self._queue
        logger.debug("connection is {!r}"
                     "is connected: {!r}".format(self._conn,
                                                 self._conn.connected))
        for i in collect_replies(self._conn,
                                 self._conn.channel(),
                                 client_queue,
                                 timeout=1,
                                 limit=1,
                                 callbacks=[self.ack_message]):
            logger.info("Received {!r}".format(i))
            if self.reply is not None:
                response = self.reply
                self.reply = None
                try:
                    client_queue.purge()
                    client_queue.delete()
                    self._conn.release()
                except Exception:
                    logger.warn("Unable to purge and delete queues",
                                exc_info=True)
                return response

    def ack_message(self, body, message):
        logger.info("Processing message: {!r} with body {!r}".format(message,
                                                                     body))
        if 'correlation_id' in message.properties:
            corr_id = message.properties['correlation_id']
            try:
                self.messages.pop(corr_id)
                server_queue = self.corr_id_server_queue.pop(corr_id)
                logger.info(
                    "STOPREQUEST:%s;CORRELATION_ID:%s" %
                    (server_queue, corr_id))
                self.reply = body
                message.ack()
            except KeyError as e:
                logger.exception(e)
                logger.error("Malformed message: {!r}".format(body))

    def _setup_payload(self, command_name, data):
        """Setup the datastructure for either hase-like or standard.

        :command_name: the name of the command
        :data: data to be sent with the command
        :returns: payload for the request

        """
        if self._legacy:
            payload = {
                'data': {
                    'command': command_name,
                    'options': data,
                }
            }
        else:
            payload = data
        return payload

    def _prepare_client_queue(self, command_name):
        """Setup a client queue based on the command.

        """
        if self._client_queue is None:
            self._client_queue = '.'.join([command_name, 'client'])

    def rpc(self,
            command_name,
            data={},
            server_routing_key=None):
        """Send a RPC request

        :command_name: the command to execute (used as routing key)
        :data: dict with data to be sent
        :client_queue: Queue for this particular request
        :server_routing_key: Server routing key. Will
        default to <command>.server
        """

        self.reply_received = False
        payload = self._setup_payload(command_name, data)
        logger.info("Preparing request {!r}".format(payload))

        if server_routing_key is None:
            if self._prefix is None:
                server_routing_key = command_name
            else:
                server_routing_key = '.'.join([self._prefix, command_name])

        self._prepare_client_queue(command_name)
        logger.info("Set up client queue {!r} "
                    "to {!r}".format(self._client_queue,
                                     server_routing_key))

        message_correlation_id = uuid()
        properties = {
            'reply_to': self._client_queue,
            'correlation_id': message_correlation_id
        }
        self.corr_id_server_queue[message_correlation_id] = server_routing_key
        logger.info('STARTREQUEST:%s;CORRELATION_ID:%s' % (server_routing_key,
                                                           message_correlation_id))
        result = None
        try:
            self.messages[message_correlation_id] = True
            self._send_command(payload, server_routing_key, properties)
            result = self.retrieve_messages()
        except Exception as e:
            logger.debug("Whoa...something happened.")
            logger.exception(e)
            raise e
        # Successful so store message correlation id for retrieval.
        return result

    def task(self,
             command_name,
             data=None,
             server_routing_key=None):
        """Send a RPC request

        :command_name: the command to execute (used as routing key)
        :data: dict with data to be sent
        :client_queue: Queue for this particular request
        :server_routing_key: Server routing key. Will default
        to <command>.server
        """

        if data is None:
            data = {}
        self.reply_received = False
        payload = self._setup_payload(command_name, data)
        logger.info("Preparing request {!r}".format(payload))

        if server_routing_key is None:
            server_routing_key = command_name

        self._prepare_client_queue(command_name)
        logger.info("Set up client queue {!r} "
                    "to {!r}".format(self._client_queue,
                                     server_routing_key))

        self._send_command(payload, server_routing_key, declare_queue=False)

    def _send_command(self, payload, server_routing_key, properties=None,
                      declare_queue=True):
        if properties is None:
            properties = {}
        self.reply = None
        logger.info("Reply info: {!r}".format(properties))
        logger.info("Using connection: {!r}".format(CONN_DICT))
        logger.info("Declaring queue %s." % self._client_queue)
        queue = Queue(self._client_queue,
                      channel=self._conn,
                      durable=self._exchange.durable,
                      exchange=self._exchange,
                      routing_key=self._client_queue)
        if declare_queue:
            queue.declare()
        self._queue = queue
        with producers[self._conn].acquire(block=True) as producer:
            producer.publish(payload,
                             serializer='json',
                             exchange=self._exchange,
                             declare=[self._exchange],
                             routing_key=server_routing_key,
                             **properties)
            logger.info("Published to exchange "
                        "{!r}".format(self._exchange))
            logger.info("Published request %r" % payload)

if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO', loggers=[''])
    c = RpcClient(legacy=False, prefix='rabbitpy')
    c.rpc('version')

    gen = c.retrieve_messages()
    for i in gen:
        print("Response:\n\n{!r}".format(i))
