import service.control

from . import base


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'exception_action': base.ExceptionAction,
    }


class TestAction(base.TestCase):

    def setUp(self):
        super(TestAction, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple', token='test-token')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_action_exception_maps_to_code(self):
        response = self.client.call_action('exception_action', error_type=1)
        self.assertFalse(response.success)
        self.assertIn('FIRST_EXCEPTION', response.errors)
        self.assertIn('first exception', response.error_details[0].detail)

        response = self.client.call_action('exception_action', error_type=2)
        self.assertFalse(response.success)
        self.assertIn('CUSTOM_EXCEPTION', response.errors)

    def test_action_unmapped_exception_maps_to_generic_failure_with_traceback_details(self):
        response = self.client.call_action('exception_action', error_type=6)
        self.assertFalse(response.success)
        self.assertIn('SERVER_ERROR', response.errors)
        self.assertIn('NameError', response.error_details[0].detail)

    def test_action_action_errors(self):
        response = self.client.call_action('exception_action', error_type=3)
        self.assertFalse(response.success)
        self.assertIn('SIMPLE_ACTION_ERROR', response.errors)
        self.assertEqual(len(response.error_details), 0)

        response = self.client.call_action('exception_action', error_type=4)
        self.assertFalse(response.success)
        self.assertIn('ACTION_ERROR_WITH_DETAILS', response.errors)
        self.assertEqual(response.error_details[0].detail, 'details')

        response = self.client.call_action('exception_action', error_type=5)
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)
        self.assertEqual(response.error_details[0].detail, 'CUSTOM_FIELD_ERROR')
