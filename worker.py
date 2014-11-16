from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall

logger = get_logger(__name__)


class Worker(ConsumerMixin):

    def __init__(self, connection, queues):
        ConsumerMixin.__init__(self)
        self.connection = connection
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(queues=self.queues,
                     callbacks=[self.on_message],
                     accept=['json']),
        ]

    def on_message(self, body, message):
        print("RECEIVED MESSAGE: %r" % (body, ))
        message.ack()


#if __name__ == 'main':

    #from kombu import Connection, Exchange, Queue
    #from kombu.utils.debug import setup_logging

    #setup_logging(loglevel='INFO', loggers=[''])
    #with Connection(**conn_dict) as conn:
        #try:
            #worker = C(conn)
            #worker.run()
        #except KeyboardInterrupt:
            #print('bye bye')
        #except Exception as e:
            #raise
