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
        response = self.client.call_action('exception_action', first=True)
        self.assertFalse(response.success)
        self.assertIn('FIRST_EXCEPTION', response.errors)
        self.assertIn('first exception', response.error_details[0].detail)

        response = self.client.call_action('exception_action', second=True)
        self.assertFalse(response.success)
        self.assertIn('CUSTOM_EXCEPTION', response.errors)

    def test_action_unmapped_exception_maps_to_generic_failure_with_traceback_details(self):
        response = self.client.call_action('exception_action')
        self.assertFalse(response.success)
        self.assertIn('SERVER_ERROR', response.errors)
        self.assertIn('NameError', response.error_details[0].detail)
