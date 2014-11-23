import sys
from unittest import TestCase
from werkzeug.exceptions import RequestTimeout

from kombu import Connection

from rpc import conn_dict
from rpc.raygun import Raygun

class TestRaygun(TestCase):

    """Test sending stuff to raygun"""

    def setUp(self):
        """TODO: Docstring for setUp.
        :returns: TODO

        """
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
        try:
            raise RequestTimeout('Took way too long')
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            self.body['exc_type'] = exc_type
            self.body['exc_value'] = exc_value 
            self.body['exc_traceback'] = exc_traceback

            with Connection(**conn_dict) as conn:
                r = Raygun(conn)
                r.send_to_raygun(self.body)

        

