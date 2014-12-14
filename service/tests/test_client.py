import service.control
from service import exceptions

from . import base


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'simple_action': base.SimpleAction,
        'another_action': base.AnotherAction,
    }


class TestClient(base.TestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_client_call_action(self):
        action_response = self.client.call_action(
            'simple_action',
            echo='echo!',
            lurker='still here',
        )

        self.assertTrue(action_response.result.success)
        response = service.control.get_response_extension(action_response)
        self.assertEqual(response.answer, 'echo!')
        self.assertEqual(response.lurker, 'still here')

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
