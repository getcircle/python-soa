import unittest

import service.control
from service.actions import Action
from service import exceptions


class SimpleAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.echo


class AnotherAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.test


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'simple_action': SimpleAction,
        'another_action': AnotherAction,
    }


class TestClient(unittest.TestCase):

    def setUp(self):
        service.control.set_protobuf_request_registry_path(
            'service.tests.protobufs.request_registry_pb2',
        )
        service.control.set_protobuf_response_registry_path(
            'service.tests.protobufs.response_registry_pb2',
        )
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_client_call_action(self):
        response = self.client.call_action('simple_action', echo='echo!')
        import ipdb; ipdb.set_trace()
        action_response = response.actions[0]
        self.assertTrue(action_response.success)
        self.assertEqual(action_response.answer, 'echo!')

    def test_client_call_action_unrecognized_service(self):
        client = service.control.Client('invalid')
        with self.assertRaises(exceptions.UnrecognizedService):
            client.call_action('simple_action')

    def test_client_call_action_unrecognized_action(self):
        with self.assertRaises(exceptions.UnrecognizedAction):
            self.client.call_action('invalid')

    def test_client_call_action_rogue_parameter(self):
        with self.assertRaises(exceptions.RogueParameter):
            self.client.call_action('simple_action', invalid=True)
