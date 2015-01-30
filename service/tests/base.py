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


class PaginatedAction(Action):

    def run(self, *args, **kwargs):
        echos = []
        for i in range(self.request.total):
            echos.append('%s_%s' % (self.request.echo, i))
        self.paginated_response(self.response.echos, echos, lambda x, y: y.append(x))


class TestCase(unittest.TestCase):

    def setUp(self):
        service.control.set_protobufs_request_registry(
            'service.protobufs.tests.request_registry_pb2',
        )
        service.control.set_protobufs_response_registry(
            'service.protobufs.tests.response_registry_pb2',
        )
