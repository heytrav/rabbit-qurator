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

```python
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

I've included a client for posting to the RPC consumer, however it should be
possible to use any RPC client.

```python
from qurator.rpc.client import RpcClient

client = RpcClient(exchange=some_exchange)
client.rpc('do_something', {"msg": "Test"})
reply = client.retrieve_messages()

```

#General Notes

##Environment

In order to interact with RabbitMQ, you need to be sure that the following
environment variables are set when using qurator:

1. `RABBITMQ_TRANSPORT_SERVICE_HOST` (default: `localhost`)
1. `RABBITMQ_TRANSPORT_SERVICE_PORT` (default: `5672`)
1. `RABBITMQ_USER` (default: `guest`)
1. `RABBITMQ_PASSWORD`(default: `guest`)
1. `RABBITMQ_VHOST` (default: `/`)
