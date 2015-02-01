import uuid

import service.control
from service import validators
from . import base


class SimpleAction(base.SimpleAction):

    type_validators = {
        'user_id': [validators.is_uuid4],
        'echo': [lambda x: x.startswith('boo')],
    }

    field_validators = {
        'echo': {
            lambda x: x.endswith('!'): 'Must be excited',
        },
    }


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {'simple_action': SimpleAction}


class TestValidators(base.TestCase):

    def setUp(self):
        super(TestValidators, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple', token='test-token')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_failed_type_validator_results_in_error(self):
        response = self.client.call_action(
            'simple_action',
            user_id='12321313',
        )
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)

        error_detail = response.error_details[0]
        self.assertEqual(error_detail.error, 'FIELD_ERROR')
        self.assertEqual(error_detail.key, 'user_id')
        self.assertEqual(error_detail.detail, 'INVALID')

    def test_failed_type_validators_doesnt_run_feild_validators(self):
        response = self.client.call_action(
            'simple_action',
            echo='foo',
        )
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)

        self.assertEqual(len(response.error_details), 1)
        error_detail = response.error_details[0]
        self.assertEqual(error_detail.error, 'FIELD_ERROR')
        self.assertEqual(error_detail.key, 'echo')
        self.assertEqual(error_detail.detail, 'INVALID')

    def test_failed_field_validator_results_in_error(self):
        response = self.client.call_action(
            'simple_action',
            echo='boo',
        )
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)

        error_detail = response.error_details[0]
        self.assertEqual(error_detail.error, 'FIELD_ERROR')
        self.assertEqual(error_detail.key, 'echo')
        self.assertEqual(error_detail.detail, 'Must be excited')

    def test_is_uuid4_validates_uuid(self):
        response = self.client.call_action(
            'simple_action',
            user_id='123123123',
        )
        self.assertFalse(response.success)

        response = self.client.call_action(
            'simple_action',
            user_id=uuid.uuid4().hex,
        )
        self.assertTrue(response.success)
