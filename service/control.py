from protobuf_to_dict import dict_to_protobuf
from service_protobufs import soa_pb2

from . import (
    exceptions,
    registry,
    settings,
    utils,
)
from .transports import local as local_transport


class Response(object):

    def __init__(self, action_response, extension_response):
        self._action_response = action_response
        self._extension_response = extension_response

    @property
    def success(self):
        return self._action_response.result.success

    @property
    def errors(self):
        return self._action_response.result.errors

    @property
    def control(self):
        return self._action_response.control

    @property
    def error_details(self):
        return self._action_response.result.error_details

    @property
    def result(self):
        return self._extension_response


class Client(object):

    def __init__(self, service_name, post_call_action_hook=None, token=None):
        self.service_name = service_name
        self.token = token
        if isinstance(settings.DEFAULT_TRANSPORT, basestring):
            self.transport = utils.import_string(settings.DEFAULT_TRANSPORT)
        else:
            self.transport = settings.DEFAULT_TRANSPORT
        self._post_call_action_hook = post_call_action_hook or (
            lambda x: None
        )

    def set_transport(self, transport):
        self.transport = transport

    def _set_protobuf_with_list_of_dicts(self, container, values):
        for value in values:
            sub_container = container.add()
            dict_to_protobuf(value, sub_container)

    def _set_value_for_protobuf(self, protobuf, key, value):
        try:
            setattr(protobuf, key, value)
        except AttributeError:
            valid = False
            container = getattr(protobuf, key)
            if hasattr(value, 'extend') and hasattr(container, 'extend'):
                try:
                    container.extend(value)
                    valid = True
                except TypeError:
                    if all(map(lambda x: isinstance(x, dict), value)):
                        self._set_protobuf_with_list_of_dicts(container, value)
                        valid = True
            else:
                try:
                    container.CopyFrom(value)
                    valid = True
                except TypeError:
                    pass

            if not valid:
                raise exceptions.InvalidParameterValue(key, value)

    def _copy_params_to_protobuf(self, params, protobuf):
        for key, value in params.iteritems():
            if hasattr(protobuf, key):
                if isinstance(value, dict):
                    self._copy_params_to_protobuf(
                        value,
                        getattr(protobuf, key),
                    )
                else:
                    if value is not None:
                        self._set_value_for_protobuf(protobuf, key, value)
            else:
                raise exceptions.RogueParameter(key)

    def call_action(self, action_name, **params):
        service_request = soa_pb2.ServiceRequest()
        service_request.control.service = self.service_name
        if self.token is not None:
            service_request.control.token = self.token

        action_request = service_request.actions.add()
        action_request.control.service = self.service_name
        action_request.control.action = action_name
        control_params = params.pop('control', {})
        self._copy_params_to_protobuf(control_params, action_request.control)

        extension = registry.request_registry.get_extension(
            self.service_name,
            action_name,
        )
        request = action_request.params.Extensions[extension]
        self._copy_params_to_protobuf(params, request)

        service_response = self.transport.send_request(service_request)
        extension = registry.response_registry.get_extension(
            self.service_name,
            action_name,
        )
        action_response = service_response.actions[0]
        extension_response = action_response.result.Extensions[extension]
        response_wrapper = Response(action_response, extension_response)
        self._post_call_action_hook(response_wrapper)
        return response_wrapper


class Server(object):

    actions = {}
    service_name = None
    auth_exempt_actions = tuple()

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
                service_request.control,
                action_request,
                action_response,
            )
            # XXX verify this token is valid
            if (
                not service_request.control.token and
                action_request.control.action not in self.auth_exempt_actions
            ):
                action.note_error(
                    'FORBIDDEN',
                    (
                        'FORBIDDEN',
                        'authentication token must be provided for action',
                    ),
                )

            if not action.is_error():
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
