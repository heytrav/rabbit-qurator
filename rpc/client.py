from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger


from rpc import conn_dict
from rpc.queues import exchange, queues


logger = get_logger(__name__)

sent_correlation_id = uuid()
def send_as_rpc(connection, command_name, args=(), kwargs={}):
    """Send a RPC request

    :connection: Connection object
    :command_name: the command to execute (used as routing key)
    :args: args meant for command
    :kwargs: kwargs meant for command
    """
    routing_key = command_name
    payload = {
        'data': args,
        'meta': kwargs
    }

    with producers[connection].acquire(block=True) as producer:
        logger.info("Publishing request %r" % payload)
        producer.publish(payload,
                         serializer='json',
                         exchange=exchange,
                         declare=[exchange],
                         routing_key=routing_key,
                         **{
                             'reply_to': routing_key,
                             'correlation_id': sent_correlation_id
                         })

def match_correlation_id(body, message):
    """Match the correlation id sent to the one retrieved in the message. If
    it matches, 'ack' the message.

    :body: amqp request body
    :message: amqp message
    """

    logger.info("Pulling message for comparison")
    if 'correlation_id' in message.properties:
        if correlation_id == sent_correlation_id:
            logger.info("Correlation id matches")
            message.ack()


if __name__ == '__main__':
    from kombu import Connection

    with Connection(**conn_dict) as conn:
        send_as_rpc(conn, 'version', args=('Kombu', ), kwargs={})

    with Connection(**conn_dict) as conn:
        for i in collect_replies(conn,
                                 conn.channel(),
                                 queues[1],
                                 callbacks=[match_correlation_id]):
            print("Got reply: ", i)

