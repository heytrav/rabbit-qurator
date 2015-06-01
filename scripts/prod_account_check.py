
import time
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    reply = client.rpc('account_for_domain', 
               {'domains': [{"domain":'booma.wang'}]},
               server_routing_key='api.account')
    print("Got reply: {!r}".format(reply))



