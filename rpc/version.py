
from rpc.iwmnconsumer import IwmnConsumer


consumer = IwmnConsumer()

@consumer.rpc
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    with open('/etc/d8o/rabbitpy/VERSION') as f:
        version = f.read()
    return {'version': version.strip()}


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    from rpc import conn_dict
    from rpc.consumer import Worker

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])

        try:
            worker = Worker(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
