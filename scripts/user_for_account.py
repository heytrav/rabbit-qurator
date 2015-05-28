
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    client.rpc('user_for_account', 
               {'account': '4084a589401ebe665c313edecf0066a0'},
               server_routing_key='api.account')
    for reply in client.retrieve_messages():
        print("Got reply: {!r}".format(reply))



