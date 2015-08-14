from unittest import TestCase
from unittest.mock import MagicMock, ANY

from qurator.rpc.client import RpcClient


class TestClient(TestCase):

    """Test the rpc client."""

    def test_payload_standard_rpc(self):
        """Test command for standard RPC."""
        c = RpcClient()
        c._send_command = MagicMock()
        c.retrieve_messages = MagicMock()
        call_payload = {"test": 2}
        c.rpc('do_that', call_payload)
        c._send_command.assert_called_with(call_payload,
                                           'do_that',  # routing key
                                           ANY)  # properties

    def test_rpc_properties(self):
        """Test setup rpc properties.  """
        c = RpcClient(client_queue='whatever.client')
        c._send_command = MagicMock()
        c.retrieve_messages = MagicMock()
        c.rpc('whatever', {"data": "x"})
        c._send_command.assert_called_with(
            ANY,
            'whatever',
            {
                "reply_to": "whatever.client",
                "correlation_id": ANY
            }
        )
        # This part shouldn't matter if legacy or not.
        c = RpcClient(client_queue='test.my.queue')
        c._send_command = MagicMock()
        c.retrieve_messages = MagicMock()
        c.rpc('whatever', {"data": "x"})
        c._send_command.assert_called_with(
            ANY,
            'whatever',
            {
                "reply_to": "test.my.queue",
                "correlation_id": ANY
            }
        )

    def test_task_properties(self):
        """Setup task properties."""
        c = RpcClient()
        c._send_command = MagicMock()
        c.task('whatever', {"data": "x"})
        c._send_command.assert_called_with(
            ANY,
            'whatever',
            declare_queue=False
        )
        # This part shouldn't matter if legacy or not.
        c = RpcClient(client_queue='test.my.queue')
        c._send_command = MagicMock()
        c.task('whatever', {"data": "x"})
        c._send_command.assert_called_with(
            ANY,
            'whatever',
            declare_queue=False
        )
