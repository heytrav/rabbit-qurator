from kombu.pools import producers
from kombu.common import uuid, collect_replies
from kombu.log import get_logger


from rpc import conn_dict
from rpc.queues import exchange, queues
from rpc.tasks import hello_task


logger = get_logger(__name__)

def send_as_task(connection, fun, args=(), kwargs={}):
    """Send as a task

    :connection: TODO
    :fun: TODO
    :args: TODO
    :kwargs: TODO
    :returns: TODO

    """
    payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
    routing_key = 'basic'

    correlation_id = uuid()
    with producers[connection].acquire(block=True) as producer:
        logger.info("Publishing request")
        producer.publish(payload,
                         serializer='pickle',
                         exchange=exchange,
                         declare=[exchange],
                         routing_key=routing_key, 
                         **{
                             'reply_to': 'basic',
                             'correlation_id': correlation_id
                         })

if __name__ == '__main__':
    from kombu import Connection

    with Connection(**conn_dict) as conn:
        send_as_task(conn, fun=hello_task, args=('Kombu', ), kwargs={})
        for i in collect_replies(conn,
                                 conn.channel(),
                                 queues[0]):
            print("Got reply: ", i)

