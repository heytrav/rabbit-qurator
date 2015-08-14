
from qurator.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    reply = client.rpc('account_handle', 
               {'account': '1bb0db05cf3b6e6ee5ec9fcce978b0a2'},
               server_routing_key='api.account')
    print("Got reply: {!r}".format(reply))



