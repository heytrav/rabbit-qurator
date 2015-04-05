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
from rabbitpy.queuerate import Queuerator

legacy_consumer = Queuerator(queue='api.some.queue')

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
consumer = Queuerator(legacy=False,
                      prefix='awesome')

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

* `prefix` parameter to the constructor defaults to `rabbitpy`.

#General Notes

##Environment

In order to interact with RabbitMQ, you need to be sure that the following
environment variables are set when starting the docker container with
`./launch.sh`:

1. `AMQP_USER`
2. `AMQP_PASS`
3. `AMQP_VHOST`

Please refer to IWMN project documentation for `iwmn-base`, `hase`, or the
`docker_vm` repository for information on what these should be. 

##Supervisor

See config files under `supervisor/`

     supervisord -c /etc/supervisor/supervisord.conf

##Miscellaneous information
* The *hase-like* implementation is on by default.
* When using the *hase-like* implementation, a queue name is required.
* This is a work in progress and subject to unannounced sporadic changes.
