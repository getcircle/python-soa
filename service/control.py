from . import (
    exceptions,
    registry,
    settings,
    utils,
)
from .protobufs.generated import soa_pb2
from .transports import local as local_transport


class Client(object):

    def __init__(self, service_name):
        self.service_name = service_name
        self.transport = utils.import_string(settings.DEFAULT_TRANSPORT)

    def call_action(self, action_name, **params):
        service_request = soa_pb2.ServiceRequest()
        service_request.control.service = self.service_name

        action_request = service_request.actions.add()
        action_request.action = action_name

        extension = registry.request_registry.get_extension(
            self.service_name,
            action_name,
        )
        request = action_request.params.Extensions[extension]
        for key, value in params.iteritems():
            if hasattr(request, key):
                setattr(request, key, value)
            else:
                raise exceptions.RogueParameter(key)

        return self.transport.send_request(service_request)


class Server(object):

    service_name = None
    actions = {}

    def handle_request(self, serialized_request):
        service_request = soa_pb2.ServiceRequest.FromString(serialized_request)
        service_response = soa_pb2.ServiceResponse()
        service_response.control.CopyFrom(service_request.control)
        for action_request in service_request.actions:
            action_class = self.actions.get(action_request.action)
            if not action_class:
                raise exceptions.UnrecognizedAction(action_request.action)

            action_response = service_response.actions.add()
            action_response.action = action_request.action
            action = action_class(
                self.service_name,
                action_request,
                action_response,
            )
            action.execute()

        return service_response


def set_protobuf_request_registry_path(path_name):
    registry.request_registry.set_registry_path(path_name)


def set_protobuf_response_registry_path(path_name):
    registry.response_registry.set_registry_path(path_name)


def localize_server(server_class):
    local_transport.instance.localize_server(server_class)


def unlocalize_server(server_class):
    local_transport.instance.unlocalize_server(server_class)


def get_request_extension(service_name, action_request):
    extension = registry.request_registry.get_extension(
        service_name,
        action_request.action,
    )
    return action_request.params.Extensions[extension]


def get_response_extension(service_name, action_response):
    extension = registry.response_registry.get_extension(
        service_name,
        action_response.action,
    )
    return action_response.response.Extensions[extension]
