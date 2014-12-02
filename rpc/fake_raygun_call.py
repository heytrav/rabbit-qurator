import sys
import jsonpickle
from werkzeug.exceptions import RequestTimeout
from kombu import Connection, Consumer
from kombu.pools import producers

from raygun4py import raygunprovider, raygunmsgs

from rpc import conn_dict
from rabbit.exchange import exchange

body = {
    "class": 'TestRaygun',
    "version": '0.0.1',
    "user": "joe.user@ideegeo.com",
    "tags": ["test", "rabbit"],
    "keys": {
        "key1": 1111,
        "key2": 22222
    },
    "request": {
        #"headers": {
        #"Content-Type": 'application/html',
        #},
        #"hostName": "localhost",
        #"httpMethod": "GET",
        #"queryString": "",
        #"url": "http://api.iwantmyname.com",
        #"ipAddress": "73.23.44.19",
    }
}
if __name__ == '__main__':
    print("Running code.")
    try:
        raise RequestTimeout('Fake a call to the raygun task')
    except:
        print("Exception raised ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        rg_except = raygunmsgs.RaygunErrorMessage(exc_type,
                                                  exc_value,
                                                  exc_traceback,
                                                  'FakeRaygun')
        msg = raygunmsgs.RaygunMessageBuilder().new() \
            .set_machine_name('test-machine') \
            .set_version('v1.2.3') \
            .set_exception_details(rg_except) \
            .set_user(body['user']) \
            .set_tags(body['tags']) \
            .build()

        payload = jsonpickle.encode(msg, unpicklable=False)
        with Connection(**conn_dict) as conn:
            with producers[conn].acquire(block=True) as producer:
                producer.publish(payload,
                                 serializer='json',
                                 exchange=exchange,
                                 declare=[exchange],
                                 routing_key='rabbitpy.raygun')
