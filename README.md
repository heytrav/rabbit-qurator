[![Circle CI](https://circleci.com/gh/heytrav/rpc-qurator.svg?style=svg)](https://circleci.com/gh/heytrav/rpc-qurator)
#rpc-qurator

Create RabbitMQ based remote procedure call (RPC) endpoints using decorators.


#Description

This library is intended to support microservices that need to interface with
RabbitMQ.  It provides a couple wrappers that can be used to turn functions
into RPC style endpoints or fire-and-forget tasks.

#Installation

```
pip install rabbit-qurator
```

#Usage

##Consumer



```python
from qurator.queue import Qurator

q = Qurator()

@q.rpc
def do_something(data):
    """
    Process data and return a response

    :data: dict
    :return: dict
    """
    return {"message": "Hello"}

```
* By default this will create a queue called `qurator.do_something` attached
  to a direct durable exchange called `qurator`.

```
from kombu import Exchange
from qurator.queue import Qurator

exchange = Exchange('myexchange',
                    type='direct',
                    durable=False)

q = Qurator(prefix='my_queue', exchange=exchange)

@q.rpc(queue_name='test_queue')
def do_something(data):
    """
    Process data and return a response

    :data: dict
    :return: dict
    """
    return {"message": "Hello"}
```

* This will create a queue called `my_queue.test_queue` bound to `myexchange`.

##Client

You can implement clients however you like. Here is an example:
```python
from qurator.rpc.client import RpcClient

client = RpcClient(exchange=some_exchange)
client.rpc('do_something', {"msg": "Test"})
for reply in client.retrieve_messages():
    # reply somewhere in here

```


#Synopsis


Alternative method for defining queues:

```python
consumer = Qurator(prefix='awesome')

@consumer.rpc
def my_rpc_method(data);
    try:
        # do some stuff
        response = do_stuff(data)
        return response
    except Exception as e:
        return {"error": "There was an error! {!r}".format(e)}
```

This expects the client to send the following to the `awesome.my_rpc_method` queue:
```javascript
{
    "domain": "something.com",
    ...
}
```

* `prefix` parameter to the constructor defaults to `qurator`.

#General Notes

##Environment

In order to interact with RabbitMQ, you need to be sure that the following
environment variables are set when using qurator:

1. `RABBITMQ_TRANSPORT_SERVICE_HOST` (default: `localhost`)
1. `RABBITMQ_TRANSPORT_SERVICE_PORT` (default: `5672`)
1. `RABBITMQ_USER`
1. `RABBITMQ_PASS`
1. `RABBITMQ_VHOST`
