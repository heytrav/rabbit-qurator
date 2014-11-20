from kombu.log import get_logger
from rpc.consumer import RpcConsumer, rpc

logger = get_logger(__name__)

@rpc
class Version(RpcConsumer):

    """Version service"""

    def process_rpc(self, body, message):
        """Return the current rabbitpy version.

        :body: Body of message
        :message: Message object
        """
        with open('/etc/d8o/rabbitpy/VERSION') as f:
            version = f.read()
        response = {'version': version.strip()}
        self.respond_to_client(message, response)


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    from rpc import conn_dict

    setup_logging(loglevel='DEBUG', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = Version(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
