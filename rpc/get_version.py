from utils.logging import get_logger
logger = get_logger(__name__)
if __name__ == '__main__':
    from rpc.client import RpcClient
    client = RpcClient(legacy=False, prefix='rabbitpy')
    client.rpc('version')

    for i in client.retrieve_messages():
        print("Response:\n\n{!r}".format(i))
