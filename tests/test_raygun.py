import sys
import jsonpickle
from unittest import TestCase
from unittest.mock import MagicMock
from werkzeug.exceptions import RequestTimeout

from kombu import Connection, Consumer
from kombu.pools import producers

from raygun4py import raygunprovider, raygunmsgs

from rpc import conn_dict
from rpc.exchange import exchange

class TestRaygun(TestCase):

    """Test sending stuff to raygun"""

    def setUp(self):
        """Unit testy stuff.  """

        self.body = {
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


    def test_send_to_raygun(self):
        """Send a request to raygun. """

        from rpc.raygun import consumer, send_to_raygun, send

        self.assertEqual(len(consumer.queues['send_to_raygun']),
                         1,
                         'Raygun consumer listening on one queue')
        print("Consumer queues: {!r}".format(consumer))
        queues = consumer.queues['send_to_raygun']
        self.assertEqual(queues[0].name,
                         'rabbitpy.raygun',
                         'Queue named as expected')
        callbacks = consumer.callbacks['send_to_raygun']
        try:
            raise RequestTimeout('Test HTTP like exception in raygun task.')
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            rg_except = raygunmsgs.RaygunErrorMessage(exc_type,
                                                      exc_value,
                                                      exc_traceback,
                                                      'TestRaygun')
            msg = raygunmsgs.RaygunMessageBuilder().new() \
                .set_machine_name('test-machine') \
                .set_version('v1.2.3') \
                .set_exception_details(rg_except) \
                .set_user(self.body['user']) \
                .set_tags(self.body['tags']) \
                .build()

            payload = jsonpickle.encode(msg, unpicklable=False)
            with Connection(**conn_dict) as conn:
                with producers[conn].acquire(block=True) as producer:
                    producer.publish(payload,
                                     serializer='json',
                                     exchange=exchange,
                                     declare=[exchange],
                                     routing_key='rabbitpy.raygun')
        with Connection(**conn_dict) as conn:
            with Consumer(conn, queues, callbacks=callbacks):
                conn.drain_events(timeout=1) 

        send = MagicMock()
        send.assert_called()
