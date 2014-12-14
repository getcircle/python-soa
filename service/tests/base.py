import unittest

from service.actions import Action
import service.control


class SimpleAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.echo
        self.response.lurker = self.request.lurker


class AnotherAction(Action):

    def run(self, *args, **kwargs):
        self.response.answer = self.request.test


class TestCase(unittest.TestCase):

    def setUp(self):
        service.control.set_protobufs_request_registry(
            'service.protobufs.tests.request_registry_pb2',
        )
        service.control.set_protobufs_response_registry(
            'service.protobufs.tests.response_registry_pb2',
        )
