#rabbitpy

Another place for rabbits to play


#Description

Rabbits in Python. At this stage just experimental stuff.

#Setup

    docker build -t docker.domarino.com/rabbitpy .



#Running

    docker run -i -t -v /usr/local/d8o/rabbitpy:/usr/local/d8o/rabbitpy:rw docker.domarino.com/rabbitpy
    root@aa9bdd7dafab:/usr/local/d8o/rabbitpy# workon rabbitpy
    (rabbitpy)root@aa9bdd7dafab:/usr/local/d8o/rabbitpy#


#Synopsis


Create a hase like queue:
```python
from rpc.iwmnconsumer import IWMNConsumer

legacy_consumer = IWMNConsumer(queue='api.some.queue')

@legacy_consumer.rpc
def my_rpc_method(data);
    try:
        # do some stuff
        response = do_stuff(data)
        return response
    except Exception as e:
        return {"error": "There was an error! {!r}".format(e)}

```

This expects the client to send something like the following to the queue `api.some.queue`:
```javascript
{
    "command": "my_rpc_method",
    "data": {
        "domain": "something.com"
        ...
    }
}
```


Alternative method for defining queues:

```python
consumer = IWMNConsumer(legacy=False)

@consumer.rpc
def my_rpc_method(data):
def my_rpc_method(data);
    try:
        # do some stuff
        response = do_stuff(data)
        return response
    except Exception as e:
        return {"error": "There was an error! {!r}".format(e)}
```

This expects the client to send the following to the `my_rpc_method` queue:
```javascript
{
    "domain": "something.com",
    ...
}
```


#Note
* The *hase-like* implementation is on by default.
* When using the *hase-like* implementation, a queue name is required.
* This is a work in progress and subject to unannounced sporadic changes.
