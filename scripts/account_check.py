
from rabbitpy.rpc.client import RpcClient

if __name__ == '__main__':
    client = RpcClient()
    client.rpc('account_for_domain', 
               {'domains': ['1405573374-test.com']},
               server_routing_key='api.account')
    for reply in client.retrieve_messages():
        print("Got reply: {!r}".format(reply))



