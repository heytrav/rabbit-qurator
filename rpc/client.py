from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger
from amqp import exceptions


from rpc import conn_dict
from rabbit.exchange import exchange as default_exchange

logger = get_logger(__name__)


class RpcClient(object):

    """Process a RPC queue and fetch the response."""

    reply_received = False
    messages = {}

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

    def retrieve_messages(self):
        """Process the message queue and ack the one that matches the
        correlation_id sent to the server.

        :correlation_id: Expected correlation id (uuid).
        :queue: The queue to read.
        :returns: JSON object retrieved from the queue.

        """

        logger.debug("Client queue: {!r}".format(self._client_queue))
        with Connection(**conn_dict) as conn:
            client_queue = Queue(self._client_queue,
                                 durable=self._exchange.durable,
                                 exchange=self._exchange,
                                 routing_key=self._client_queue)
            logger.debug("connection is {!r}".format(conn))
            try:
                for i in collect_replies(conn,
                                         conn.channel(),
                                         client_queue,
                                         callbacks=[self.ack_message]):
                    logger.info("Received message {!r}".format(i))
                    if self.reply:
                        response = self.reply
                        self.reply = None
                        yield response
            except exceptions.AMQPError as amqp_error:
                logger.error("Unable to retreive "
                             "messages: {!r}".format(amqp_error))
            except Exception as e:
                raise e
        return None

    def ack_message(self, body, message):
        logger.info("Processing message: {!r}".format(message))
        if 'correlation_id' in message.properties:
            corr_id = message.properties['correlation_id']
            try:
                self.messages.pop(corr_id)
                self.reply = body
                message.ack()
            except KeyError as e:
                logger.info("Malformed message: ".format(e))

    def _setup_payload(self, command_name, data):
        """Setup the datastructure for either hase-like or standard.

        :command_name: the name of the command
        :data: data to be sent with the command
        :returns: payload for the request

        """
        if self._legacy:
            payload = {
                'command': command_name,
                'data': data
            }
        else:
            payload = data
        return payload

    def _prepare_client_queue(self, command_name):
        """Setup a client queue based on the command
        :returns: TODO

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
        self._send_command(payload, server_routing_key, properties)
        # Successful so store message correlation id for retrieval.
        self.messages[message_correlation_id] = True

    def task(self,
             command_name,
             data={},
             server_routing_key=None):
        """Send a RPC request

        :command_name: the command to execute (used as routing key)
        :data: dict with data to be sent
        :client_queue: Queue for this particular request
        :server_routing_key: Server routing key. Will default
        to <command>.server
        """

        self.reply_received = False
        payload = self._setup_payload(command_name, data)
        logger.info("Preparing request {!r}".format(payload))

        if server_routing_key is None:
            server_routing_key = command_name

        self._prepare_client_queue(command_name)
        logger.info("Set up client queue {!r} "
                    "to {!r}".format(self._client_queue,
                                     server_routing_key))

        self._send_command(payload, server_routing_key)

    def _send_command(self, payload, server_routing_key, properties=None):
        if properties is None:
            properties = {}
        logger.info("Reply info: {!r}".format(properties))
        with Connection(**conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                try:
                    producer.publish(payload,
                                     serializer='json',
                                     exchange=self._exchange,
                                     declare=[self._exchange],
                                     routing_key=server_routing_key,
                                     **properties)
                    logger.info("Published to exchange "
                                "{!r}".format(self._exchange))
                    logger.info("Published request %r" % payload)
                except Exception as e:
                    logger.error("Unable to publish to queue: {!r}".format(e))
                    raise


if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO', loggers=[''])
    c = RpcClient(legacy=False, prefix='rabbitpy')
    c.rpc('version')

    gen = c.retrieve_messages()
    for i in gen:
        print("Response:\n\n{!r}".format(i))
