
from rabbit.queuerate import Queuerator


consumer = Queuerator(legacy=False)

def retrieve_version():
    """Retrieve the version of the rabbitpy application.
    :returns: str representing the app version

    """
    with open('/etc/d8o/rabbitpy/VERSION') as f:
        version = f.read()
    return version.strip()
    


@consumer.rpc(queue_name='')
def version(*args, **kwargs):
    """Return the current rabbitpy version."""
    return {'version': retrieve_version()}


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging

    from rpc import conn_dict
    from rabbit.worker import Worker

    with Connection(**conn_dict) as conn:
        setup_logging(loglevel='DEBUG', loggers=[''])

        try:
            worker = Worker(conn, consumer)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
