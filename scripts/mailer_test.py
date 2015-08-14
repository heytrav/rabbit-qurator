
import time
from qurator.exchange import task_exchange
from qurator.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient(exchange=task_exchange)
    reply = client.task('missing_handle', 
               {'user_id': "4084a589401ebe665c313edecf001fcb"},
               server_routing_key='api.mailer')
    print("Got reply: {!r}".format(reply))



