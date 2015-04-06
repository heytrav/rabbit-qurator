import sys
import jsonpickle
from unittest import TestCase
from unittest.mock import MagicMock
from werkzeug.exceptions import RequestTimeout

from kombu import Connection, Consumer, Exchange, Queue
from kombu.pools import producers

from raygun4py import raygunprovider, raygunmsgs

from rabbitpy.rpc import CONN_DICT
from rabbitpy.exchange import task_exchange

from tests.test_rabbit import TestRabbitpy


class TestRaygun(TestRabbitpy):

    """Test sending stuff to raygun"""

    def setUp(self):
        """Unit testy stuff.  """

        TestRabbitpy.setUp(self)
        self.queues = [
            Queue('test.raygun',
                  task_exchange,
                  durable=task_exchange.durable,
                  channel=self._connection,
                  routing_key='test.raygun')
        ]
        [i.declare(0) for i in self.queues]

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
                "headers": {
                    "content-type": 'application/html',
                },
                "hostname": "localhost",
                "httpmethod": "get",
                "querystring": "",
                "url": "http://api.iwantmyname.com",
                "ipaddress": "73.23.44.19",
            }
        }

    def test_send_to_raygun(self):
        """Send a request to raygun. """

        from rabbitpy.service.raygun import q, send

        @q.task(queue_name='test.raygun')
        def test_raygun(data):
            send(data)

        self.assertEqual(len(q.queues['test_raygun']),
                         1,
                         'Raygun q listening on one queue')
        print("Consumer queues: {!r}".format(q))
        queues = q.queues['test_raygun']
        self.assertEqual(queues[0].name,
                         'test.raygun',
                         'Queue named as expected')
        callbacks = q.callbacks['test_raygun']
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
            with Connection(**CONN_DICT) as conn:
                with producers[conn].acquire(block=True) as producer:
                    producer.publish(payload,
                                     serializer='json',
                                     exchange=task_exchange,
                                     declare=[task_exchange],
                                     routing_key='test.raygun')
        with Connection(**CONN_DICT) as conn:
            with Consumer(conn, queues, callbacks=callbacks):
                conn.drain_events(timeout=1)

        send = MagicMock()
        send.assert_called()
