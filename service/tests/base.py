import unittest

from service.actions import Action
import service.control
from service.protobufs.tests.simple_service import exception_action_pb2


class SimpleAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.echo
        self.response.lurker = self.request.lurker


class AnotherAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.test


class PaginatedAction(Action):

    def run(self, *args, **kwargs):
        echos = []
        for i in range(self.request.total):
            echos.append('%s_%s' % (self.request.echo, i))
        self.paginated_response(self.response.echos, echos, lambda x, y: y.append(x))


class ExceptionAction(Action):

    class CustomException(Exception):
        """custom exception"""

    exception_to_error_map = {
        ValueError: 'FIRST_EXCEPTION',
        CustomException: 'CUSTOM_EXCEPTION',
    }

    def run(self, *args, **kwargs):
        if self.request.error_type == exception_action_pb2.VALUE_ERROR:
            raise ValueError('first exception')
        elif self.request.error_type == exception_action_pb2.CUSTOM_ERROR:
            raise ExceptionAction.CustomException('custom exception')
        elif self.request.error_type == exception_action_pb2.ACTION_ERROR:
            raise self.ActionError('SIMPLE_ACTION_ERROR')
        elif self.request.error_type == exception_action_pb2.ACTION_ERROR_WITH_DETAILS:
            raise self.ActionError('ACTION_ERROR_WITH_DETAILS', ('ACTION_ERROR', 'details'))
        elif self.request.error_type == exception_action_pb2.ACTION_FIELD_ERROR:
            raise self.ActionFieldError('error_type', 'CUSTOM_FIELD_ERROR')
        elif self.request.error_type == exception_action_pb2.UNMAPPED_ERROR:
            raise NameError('unmapped exception')


class RequiredFieldsAction(Action):

    required_fields = ('required_field',)

    def run(self, *args, **kwargs):
        self.response.required_field = self.request.required_field
        self.response.optional_field = self.request.optional_field


class TestCase(unittest.TestCase):

    def setUp(self):
        service.control.set_protobufs_request_registry(
            'service.protobufs.tests.request_registry_pb2',
        )
        service.control.set_protobufs_response_registry(
            'service.protobufs.tests.response_registry_pb2',
        )
