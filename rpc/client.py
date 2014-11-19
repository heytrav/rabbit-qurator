from kombu import Queue, Connection
from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger


from rpc import conn_dict
from rpc.exchange import exchange

logger = get_logger(__name__)

def send_command(command_name, 
                data={}, 
                server_queue=None,
                client_queue=None):
    """Send a RPC request

    :command_name: the command to execute (used as routing key)
    :data: dict with data to be sent
    :server_queue: queue to send this to. 
    """

    payload = {
        'command': command_name,
        'data': data
    }
    logger.info("Preparing request {!r}".format(payload))

    if not server_queue:
        server_queue = '_'.join([command_name, 'server_queue'])

    if not client_queue:
        route_name = '_'.join([command_name, 'client'])
        queue_name = '_'.join([route_name, 'queue'])
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
                                routing_key=server_queue,
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
        for i in collect_replies(conn,
                                 conn.channel(),
                                 client_queue,
                                 callbacks=[ack_message]):
            print("Got message {!r}".format(i))
            return i




if __name__ == '__main__':
    response = send_command('version')
    print("Got response: {!r}".format(response))
