import uuid

import service.control
from service import validators
from . import base


class SimpleAction(base.SimpleAction):

    field_validators = {
        'user_id': {
            validators.is_uuid4: 'INVALID',
        },
    }


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {'simple_action': SimpleAction}


class TestValidators(base.TestCase):

    def setUp(self):
        super(TestValidators, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_failed_validation_results_in_error(self):
        action_response = self.client.call_action(
            'simple_action',
            user_id='12321313',
        )
        self.assertFalse(action_response.result.success)
        self.assertIn('FIELD_ERROR', action_response.result.errors)

        error_detail = action_response.result.error_details[0]
        self.assertEqual(error_detail.error, 'FIELD_ERROR')
        self.assertEqual(error_detail.key, 'user_id')
        self.assertEqual(error_detail.detail, 'INVALID')

    def test_is_uuid4_validates_uuid(self):
        action_response = self.client.call_action(
            'simple_action',
            user_id='123123123',
        )
        self.assertFalse(action_response.result.success)

        action_response = self.client.call_action(
            'simple_action',
            user_id=uuid.uuid4().hex,
        )
        self.assertTrue(action_response.result.success)
