from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger
from amqp import exceptions


from rpc import conn_dict
from rpc.exchange import exchange as default_exchange

logger = get_logger(__name__)


class RpcClient(object):
    """Process a RPC queue and fetch the response."""

    reply_received = False
    messages = {}

    def __init__(self,
                 exchange=default_exchange,
                 client_queue=None):
        """Constructor for client object. """
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
            logger.debug("connection is {!r}".format(conn))
            try:
                for i in collect_replies(conn,
                                         conn.channel(),
                                         self._client_queue,
                                         callbacks=[self.ack_message]):
                    logger.info("Received message {!r}".format(i))
                    if self.reply:
                        response = self.reply
                        self.reply = None
                        yield response
            except exceptions.AMQPError as amqp_error:
                logger.error("Unable to retreive messages: {!r}".format(amqp_error))
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
                #self.reply_queue.append(body)
                message.ack()
            except KeyError as e:
                logger.info("Could not find {!r} in messages".format(corr_id))


    def rpc(self,
            command_name,
            data={},
            server_routing_key=None):
        """Send a RPC request

        :command_name: the command to execute (used as routing key)
        :data: dict with data to be sent
        :client_queue: Queue for this particular request
        :server_routing_key: Server routing key. Will default to <command>.server
        """

        self.reply_received = False
        payload = {
            'command': command_name,
            'data': data
        }
        logger.info("Preparing request {!r}".format(payload))

        if server_routing_key is None:
            server_routing_key = '.'.join([command_name])

        if self._client_queue is None:
            queue_name = '.'.join(['rabbitpy', command_name, 'client'])
            route_name = '.'.join([command_name, 'client'])
            self._client_queue = Queue(queue_name,
                                 self._exchange,
                                 durable=False,
                                 routing_key=route_name)
        logger.info("Set up client queue {!r} to {!r}".format(self._client_queue,
                                                              server_routing_key))


        message_correlation_id = uuid()
        properties = {
            'reply_to': self._client_queue.routing_key,
            'correlation_id': message_correlation_id
        }
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
                    self.messages[message_correlation_id] = True
                    logger.info("Published to exchange {!r}".format( self._exchange))
                    logger.info("Published request %r" % payload)
                except Exception as e:
                    logger.error("Unable to publish to queue: {!r}".format(e))
                    raise


if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO', loggers=[''])
    c = RpcClient()
    msg_id = c.rpc('version' )
    response = c.retrieve_messages()
    print("Got response: {!r}".format(response))
