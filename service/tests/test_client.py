import service.control
from service import exceptions

from . import base


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'simple_action': base.SimpleAction,
        'another_action': base.AnotherAction,
    }


class AuthExemptServer(SampleServer):
    auth_exempt_actions = ('simple_action',)


class TestClient(base.TestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple', token='test-token')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_client_call_action(self):
        response = self.client.call_action(
            'simple_action',
            echo='echo!',
            lurker='still here',
        )

        self.assertTrue(response.success)
        self.assertEqual(response.result.answer, 'echo!')
        self.assertEqual(response.result.lurker, 'still here')

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

    def test_client_call_action_nested_params(self):
        response = self.client.call_action(
            'another_action',
            test='test',
            nested={'echo': 'echo!'},
        )
        self.assertTrue(response.success)


class TestAuthExemptActions(base.TestCase):

    def setUp(self):
        super(TestAuthExemptActions, self).setUp()
        service.control.localize_server(AuthExemptServer)
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.unlocalize_server(AuthExemptServer)

    def test_client_call_auth_exempt_action(self):
        response = self.client.call_action(
            'simple_action',
            echo='echo!',
        )

        self.assertTrue(response.success)
        self.assertEqual(response.result.answer, 'echo!')

    def test_client_non_auth_exempt_action(self):
        response = self.client.call_action(
            'another_action',
            test='test',
        )
        self.assertFalse(response.success)
        self.assertIn('FORBIDDEN', response.errors)
