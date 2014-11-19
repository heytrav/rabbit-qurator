import os
from rpc import RpcConsumer, RpcCall


@RpcCall
def hello():
    return {'message': 'Hello, World!'}


@RpcCall
def version():
    return {'version': os.environ['VERSION']}



if __name__ == '__main__' :
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    from rpc import conn_dict

    setup_logging(loglevel='INFO', loggers=[''])
    with Connection(**conn_dict) as conn:
        try:
            worker = RpcConsumer(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
