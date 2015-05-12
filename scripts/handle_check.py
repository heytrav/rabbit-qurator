

from kombu import Exchange
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    client.rpc('get_handle', 
               {'handle_id': '001bffe546d6705f4e004a80e30769bd'},
               server_routing_key='api.handle')
    for reply in client.retrieve_messages():
        print("Got reply: {!r}".format(reply))



