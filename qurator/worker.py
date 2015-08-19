from kombu.mixins import ConsumerMixin
from . import get_logger

logger = get_logger(__name__)


class Worker(ConsumerMixin):

    """Manage server side of RPC connection.

    This code is based on the examples on the Kombu website.
    """

    def __init__(self, connection, consumer):
        """Worker(connection)

        :connection: Connection object
        """
        logger.debug("Called constructor.")
        self.connection = connection
        self.consumer = consumer

    def get_consumers(self, Consumer, channel):
        """Get a set of consumers.

        :Consumer: Consumer object
        :channel: a channel
        :returns: array of Consumer objects

        """
        consumer_set = []
        for i in self.consumer.queues.keys():
            queues = self.consumer.queues[i]
            callbacks = self.consumer.callbacks[i]
            logger.info("Queues: {!r}".format(queues))
            c = Consumer(queues, callbacks=callbacks)
            consumer_set.append(c)
            logger.info("Added consumer: {!r}".format(c))

        logger.info("Called get_consumers with {!r}".format(consumer_set))
        return consumer_set
