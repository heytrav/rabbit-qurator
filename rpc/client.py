from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger
from amqp import exceptions


from rpc import conn_dict
from rpc.exchange import exchange as default_exchange

logger = get_logger(__name__)

def send_command(command_name,
                data={},
                server_routing_key=None,
                client_queue=None,
                exchange=None):
    """Send a RPC request

    :command_name: the command to execute (used as routing key)
    :data: dict with data to be sent
    :server_routing_key: Server routing key. Will default to <command>.server
    :client_queue: Queue to reply to. 
    """

    payload = {
        'command': command_name,
        'data': data
    }
    logger.info("Preparing request {!r}".format(payload))

    if not exchange:
        exchange = default_exchange

    if not server_routing_key:
        server_routing_key = '.'.join([command_name, 'server'])

    if not client_queue:
        queue_name = '.'.join(['rabbitpy', command_name, 'client'])
        route_name = '.'.join([command_name, 'client'])
        client_queue = Queue(queue_name,
                            exchange,
                            routing_key=route_name)
        logger.info("Set up client queue {!r}".format(client_queue))

    message_correlation_id = uuid()
    properties = {
        'reply_to': client_queue.routing_key,
        'correlation_id': message_correlation_id
    }
    logger.info("Reply info: {!r}".format(properties))
    with Connection(**conn_dict) as connection:
        with producers[connection].acquire(block=True) as producer:
            logger.info("Publishing request %r" % payload)
            try:
                producer.publish(payload,
                                serializer='json',
                                exchange=exchange,
                                declare=[exchange],
                                routing_key=server_routing_key,
                                 **properties)
            except Exception as e:
                logger.error("Unable to publish to queue: {!r}".format(e))
                raise

    def ack_message(body, message):
        logger.info("Processing message: {!r}".format(message))
        if 'correlation_id' in message.properties:
            if message.properties['correlation_id'] == message_correlation_id:
                message.ack()

    with Connection(**conn_dict) as conn:
        
        try:
            for i in collect_replies(conn,
                                    conn.channel(),
                                    client_queue,
                                    callbacks=[ack_message]):
                print("Got message {!r}".format(i))
                return i
        except exceptions.AMQPError as amqp_error:
            logger.error("Unable to retreive messages: {!r}".format(amqp_error))
        except Exception as e:
            raise e




if __name__ == '__main__':
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO', loggers=[''])
    response = send_command('version')
    print("Got response: {!r}".format(response))
