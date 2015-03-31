import service.control

from . import base


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'exception_action': base.ExceptionAction,
        'required_fields_action': base.RequiredFieldsAction,
    }


class TestAction(base.TestCase):

    def setUp(self):
        super(TestAction, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple', token='test-token')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_action_exception_maps_to_code(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=1)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FIRST_EXCEPTION', response.errors)
        self.assertIn('first exception', response.error_details[0].detail)

        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=2)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('CUSTOM_EXCEPTION', response.errors)

    def test_action_unmapped_exception_maps_to_generic_failure_with_traceback_details(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=6)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('SERVER_ERROR', response.errors)
        self.assertIn('NameError', response.error_details[0].detail)

    def test_action_action_errors(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=3)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('SIMPLE_ACTION_ERROR', response.errors)
        self.assertEqual(len(response.error_details), 0)

        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=4)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('ACTION_ERROR_WITH_DETAILS', response.errors)
        self.assertEqual(response.error_details[0].detail, 'details')

        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('exception_action', error_type=5)

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)
        self.assertEqual(response.error_details[0].detail, 'CUSTOM_FIELD_ERROR')

    def test_action_required_field(self):
        response = self.client.call_action(
            'required_fields_action',
            required_repeated_field=['required'],
            required_field='required',
            required_container={
                'required_field': 'required',
            },
        )
        self.assertEqual(response.result.required_field, 'required')
        self.assertEqual(response.result.required_repeated_field, ['required'])
        self.assertEqual(response.result.required_container.required_field, 'required')

    def test_action_required_field_missing(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('required_fields_action', required_repeated_field=['required'])

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)
        self.assertEqual(response.error_details[0].detail, 'MISSING')
        self.assertEqual(response.error_details[0].key, 'required_field')

    def test_action_required_field_missing_repeated_field(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action('required_fields_action', required_field='required')

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)
        self.assertEqual(response.error_details[0].detail, 'MISSING')
        self.assertEqual(response.error_details[0].key, 'required_repeated_field')

    def test_action_required_field_missing_required_container_required_field(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action(
                'required_fields_action',
                required_field='required',
                required_repeated_field=['required'],
            )

        response = expected.exception.response
        self.assertIn('FIELD_ERROR', response.errors)
        self.assertEqual(response.error_details[0].detail, 'MISSING')
        self.assertEqual(response.error_details[0].key, 'required_container.required_field')
