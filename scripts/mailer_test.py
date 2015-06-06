
import time
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    reply = client.rpc('account_for_domain', 
               {'user_id': "4084a589401ebe665c313edecf001fcb"},
               server_routing_key='api.mailer')
    print("Got reply: {!r}".format(reply))



