

from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    client.rpc('personal_handle', 
               {'handle_id ': '30e8e78c61fc0941aeff87654f0001b2'},
               server_routing_key='api.handle')
    for reply in client.retrieve_messages():
        print("Got reply: {!r}".format(reply))



