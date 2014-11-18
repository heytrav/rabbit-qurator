from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger


from rpc import conn_dict
from rpc.queues import consumer_exchange, client_queues

logger = get_logger(__name__)

def send_as_rpc(connection, command_name, args=(), kwargs={}):
    """Send a RPC request

    :connection: Connection object
    :command_name: the command to execute (used as routing key)
    :args: args meant for command
    :kwargs: kwargs meant for command
    """
    payload = {
        'command': command_name,
        'meta': kwargs
    }

    message_correlation_id = uuid()
    with producers[connection].acquire(block=True) as producer:
        logger.info("Publishing request %r" % payload)
        producer.publish(payload,
                         serializer='json',
                         exchange=consumer_exchange,
                         declare=[consumer_exchange],
                         routing_key='server_hello',
                         **{
                             'reply_to': 'client_hello',
                             'correlation_id': message_correlation_id
                         })
    return message_correlation_id


def check_correlation_id(sent_corr_id, message):
    """Compare the id received with the one we sent.

    :sent_corr_id: The correlation id we sent.
    :message: The message received from the server.
    """
    logger.info("Checking correlation id %r" % message.properties)
    if 'correlation_id' in message.properties:
        correlation_id = message.properties['correlation_id']
        if correlation_id == sent_corr_id:
            message.ack()


if __name__ == '__main__':
    from kombu import Connection

    with Connection(**conn_dict) as conn:
        message_correlation_id = send_as_rpc(conn, 'hello', args=('Kombu', ), kwargs={})
        print("Message correlation id %s" % message_correlation_id)

    def check_correlation(body, message):
        check_correlation_id(message_correlation_id, message)

    with Connection(**conn_dict) as conn:
        for i in collect_replies(conn,
                                 conn.channel(),
                                 client_queues[0],
                                 callbacks=[check_correlation]):
            print("Got reply: ", i)
