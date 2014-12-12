import unittest

import service.control
from service.actions import Action

from .protobufs import simple_action_pb2


class SimpleAction(Action):
    request_class = simple_action_pb2.Request
    response_class = simple_action_pb2.Response

    def run(self, *args, **kwargs):
        self.response.answer = self.request.echo


class TestClient(unittest.TestCase):

    def setUp(self):
        service.control.registry.register_action(
            service_name='simple',
            action_name='simple_action',
            action_class=SimpleAction,
        )
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.registry.flush()

    def test_client_call_action(self):
        response = self.client.call_action('simple_action', echo='echo!')
        action_response = response.actions[0]
        self.assertTrue(action_response.success)
        self.assertEqual(action_response.answer, 'echo!')

    def test_client_call_action_unrecognized_service(self):
        client = service.control.Client('invalid')
        with self.assertRaises(service.control.UnrecognizedService):
            client.call_action('simple_action')

    def test_client_call_action_unrecognized_action(self):
        with self.assertRaises(service.control.UnrecognizedAction):
            self.client.call_action('invalid')

    def test_client_call_action_rogue_parameter(self):
        with self.assertRaises(service.control.RogueParameter):
            self.client.call_action('simple_action', invalid=True)
