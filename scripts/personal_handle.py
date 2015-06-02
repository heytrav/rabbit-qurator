

from kombu import Exchange
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    reply = client.rpc('personal_handle', 
               {"handles": {"personal":{'id': '001bffe546d6705f4e004a80e30769bd'}}},
               server_routing_key='api.handle')
    print("Got reply: {!r}".format(reply))



