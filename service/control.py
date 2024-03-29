import logging

from protobuf_to_dict import (
    dict_to_protobuf,
    protobuf_to_dict,
)
from service_protobufs import soa_pb2

from . import (
    exceptions,
    metrics,
    registry,
    settings,
    utils,
)
from .transports import local as local_transport


class Response(object):

    def __init__(self, service_response, action_response, extension_response):
        self.service_response = service_response
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


class CallActionError(Exception):
    def __init__(self, response=None, service_response=None, exception=None, *args, **kwargs):
        self.response = response
        self.service_response = service_response
        self.exception = exception
        super(CallActionError, self).__init__(self.summary, *args, **kwargs)

    @property
    def summary(self):
        if self.response:
            return 'ERROR: %s.%s\n%s' % (
                self.response.control.service,
                self.response.control.action,
                self.generate_error_summary(),
            )
        elif self.service_response:
            return 'ERROR: %s:%s' % (
                self.service_response.control.service,
                str(self.exception),
            )

    def generate_error_summary(self):
        summary = ''
        if self.response.errors:
            summary += 'errors: %s\n' % ('\n  -'.join(self.response.errors))
        if self.response.error_details:
            summaries = ['%s:%s:%s' % (detail.error, detail.key, detail.detail) for detail
                         in self.response.error_details]
            summary += 'error_details: %s\n' % ('\n   -'.join(summaries))
        return summary


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

    def _build_request(self, action_name, **params):
        service_request = soa_pb2.ServiceRequestV1()
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
        return service_request

    def _send_request(self, action, service_request, on_error=None):
        service_response = self.transport.send_request(service_request)
        extension = registry.response_registry.get_extension(
            self.service_name,
            action,
        )
        try:
            action_response = service_response.actions[0]
        except IndexError as e:
            raise CallActionError(service_response=service_response, exception=e)

        extension_response = action_response.result.Extensions[extension]
        response_wrapper = Response(service_response, action_response, extension_response)
        self._post_call_action_hook(response_wrapper)
        if not response_wrapper.success:
            if isinstance(on_error, Exception):
                raise on_error
            raise CallActionError(response_wrapper)
        return response_wrapper

    def call_action(self, action, on_error=None, **params):
        service_request = self._build_request(action, **params)
        return self._send_request(action, service_request, on_error=on_error)

    def call(self, action, action_kwargs, on_error=None):
        service_request = self._build_request(action, **action_kwargs)
        return self._send_request(action, service_request, on_error=on_error)

    def get_object(self, action, return_object, **action_kwargs):
        response = self.call_action(action, **action_kwargs)
        return getattr(response.result, return_object)


class Server(object):

    actions = {}
    service_name = None
    auth_exempt_actions = tuple()

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger('services.%s' % (self.service_name,))
        return self._logger

    def record_message_received(self, service_request):
        if settings.LOG_REQUEST_AND_RESPONSE:
            self.logger.info('recv: %s', protobuf_to_dict(service_request))

    def record_message_sent(self, service_response):
        if settings.LOG_REQUEST_AND_RESPONSE:
            self.logger.info('sent: %s', protobuf_to_dict(service_response))

    def get_action_class(self, control, action):
        action_class = self.actions.get(action)
        return action_class

    @metrics.count('service.request.count')
    @metrics.time('service.response.time')
    def handle_request(self, serialized_request):
        with metrics.time('service.%s.response.time' % (self.service_name,)):
            return self._handle_request(serialized_request)

    def _handle_request(self, serialized_request):
        with metrics.time('service.request.deserialization.time'):
            service_request = soa_pb2.ServiceRequestV1.FromString(serialized_request)

        self.record_message_received(service_request)
        service_response = soa_pb2.ServiceResponseV1()
        service_response.control.CopyFrom(service_request.control)
        for action_request in service_request.actions:
            action_class = self.get_action_class(
                service_request.control,
                action_request.control.action,
            )
            if not action_class:
                raise exceptions.UnrecognizedAction(
                    action_request.control.action,
                )

            action_response = service_response.actions.add()
            action_response.control.CopyFrom(action_request.control)
            action = action_class(
                service_response.control,
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
                metric_name = 'service.%s.action.%s' % (
                    self.service_name,
                    action_request.control.action,
                )
                metrics.increment('%s.%s' % (metric_name, 'count'))
                with metrics.time('%s.%s' % (metric_name, 'time')):
                    action.execute()

            if not action_response.result.errors:
                action_response.result.success = True

        self.record_message_sent(service_response)
        return service_response


def set_protobufs_request_registry(path_name_or_registry):
    registry.request_registry.set_registry(path_name_or_registry)


def set_protobufs_response_registry(path_name_or_registry):
    registry.response_registry.set_registry(path_name_or_registry)


def set_metrics_handler(handler):
    metrics._instance = handler


def start_metrics_handler(*args, **kwargs):
    metrics.start(*args, **kwargs)


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


def get_object(service, action, return_object, client_kwargs=None, **action_kwargs):
    response = call_action(service, action, client_kwargs=client_kwargs, **action_kwargs)
    return getattr(response.result, return_object)


def call_action(service, action, client_kwargs=None, **action_kwargs):
    client_kwargs = client_kwargs or {}
    client = Client(service, **client_kwargs)
    return client.call_action(action, **action_kwargs)


def call(service, action, client_kwargs, action_kwargs):
    client_kwargs = client_kwargs or {}
    client = Client(service, **client_kwargs)
    return client.call(action, action_kwargs)


def update_paginator_protobuf(protobuf, paginator, page):
    protobuf.count = paginator.count
    protobuf.total_pages = paginator.num_pages
    if page.has_next():
        protobuf.next_page = page.next_page_number()
    else:
        protobuf.ClearField('next_page')

    if page.has_previous():
        protobuf.previous_page = page.previous_page_number()
    else:
        protobuf.ClearField('previous_page')
