from . import (
    exceptions,
    registry,
    settings,
    utils,
)
from .protobufs.common import soa_pb2
from .transports import local as local_transport


class Client(object):

    def __init__(self, service_name):
        self.service_name = service_name
        self.transport = utils.import_string(settings.DEFAULT_TRANSPORT)

    def set_transport(self, transport):
        self.transport = transport

    def call_action(self, action_name, **params):
        service_request = soa_pb2.ServiceRequest()
        service_request.control.service = self.service_name

        action_request = service_request.actions.add()
        action_request.control.service = self.service_name
        action_request.control.action = action_name

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

        service_response = self.transport.send_request(service_request)
        extension = registry.response_registry.get_extension(
            self.service_name,
            action_name,
        )
        action_response = service_response.actions[0]
        response = action_response.result.Extensions[extension]
        return action_response, response


class Server(object):

    service_name = None
    actions = {}

    def handle_request(self, serialized_request):
        service_request = soa_pb2.ServiceRequest.FromString(serialized_request)
        service_response = soa_pb2.ServiceResponse()
        service_response.control.CopyFrom(service_request.control)
        for action_request in service_request.actions:
            action_class = self.actions.get(action_request.control.action)
            if not action_class:
                raise exceptions.UnrecognizedAction(
                    action_request.control.action,
                )

            action_response = service_response.actions.add()
            action_response.control.CopyFrom(action_request.control)
            action = action_class(
                self.service_name,
                action_request,
                action_response,
            )
            action.execute()
            if not action_response.result.errors:
                action_response.result.success = True

        return service_response


def set_protobufs_request_registry(path_name_or_registry):
    registry.request_registry.set_registry(path_name_or_registry)


def set_protobufs_response_registry(path_name_or_registry):
    registry.response_registry.set_registry(path_name_or_registry)


def localize_server(server_class):
    local_transport.instance.localize_server(server_class)


def unlocalize_server(server_class):
    local_transport.instance.unlocalize_server(server_class)


def get_request_extension(action_request):
    extension = registry.request_registry.get_extension(
        action_request.control.service,
        action_request.control.action,
    )
    return action_request.params.Extensions[extension]


def get_response_extension(action_response):
    extension = registry.response_registry.get_extension(
        action_response.control.service,
        action_response.control.action,
    )
    return action_response.result.Extensions[extension]
