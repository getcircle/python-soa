import json
import logging
from md5 import md5
import re

from google.protobuf import message
from protobuf_to_dict import (
    dict_to_protobuf,
    protobuf_to_dict,
)
from service_protobufs import soa_pb2

from .. import control
from .base import BaseTransport
from .local import instance as local_instance


class MockTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(MockTransport, self).__init__(*args, **kwargs)
        self.mock_responses = {}
        self.mock_regex_lookups = {}
        self.mocked_calls = []
        self._dont_mock_services = set()

    def _get_params_hash(self, params):
        ordered_params = sorted(params.items(), key=lambda x: x[0])
        ordered = []
        for key, value in ordered_params:
            if isinstance(value, list):
                value.sort()
            ordered.append((key, value))

        serializable = []
        for key, value in ordered:
            if isinstance(value, message.Message):
                serializable.append((key, protobuf_to_dict(value)))
            else:
                serializable.append((key, value))
        result = md5(json.dumps(serializable)).hexdigest()
        return result

    def _get_mock_key(self, service, action, params):
        return '%s:%s:%s' % (
            service,
            action,
            self._get_params_hash(params),
        )

    def clear(self):
        self.mock_responses = {}
        self.mock_regex_lookups = {}
        self.mocked_calls = []
        self._dont_mock_services = set()

    def dont_mock_service(self, service):
        self._dont_mock_services.add(service)

    def register_mock_error(
            self,
            service,
            action,
            error,
            mock_regex_lookup=False,
            **params
        ):
        mock_key = self._get_mock_key(service, action, params)
        self.mock_responses[mock_key] = (error, False)
        if mock_regex_lookup:
            self.mock_regex_lookups[mock_regex_lookup] = (error, False)

    def register_mock_call_action_error(
            self,
            service,
            action,
            errors=None,
            error_details=None,
            mock_regex_lookup=False,
            **params
        ):
        error = get_mockable_call_action_error(
            service=service,
            action=action,
            errors=errors,
            error_details=error_details,
        )
        self.register_mock_error(
            service=service,
            action=action,
            error=error,
            mock_regex_lookup=mock_regex_lookup,
            **params
        )

    def register_empty_response(self, service, action, mock_regex_lookup=None, **params):
        mock_response = get_mockable_response(service, action)
        self.register_mock_response(
            service,
            action,
            mock_response,
            mock_regex_lookup=mock_regex_lookup,
            **params
        )

    def register_mock_object(
            self,
            service,
            action,
            return_object_path,
            return_object,
            mock_regex_lookup=None,
            **params
        ):
        mock_response = get_mockable_response(service, action)
        if hasattr(getattr(mock_response, return_object_path), 'CopyFrom'):
            getattr(mock_response, return_object_path).CopyFrom(return_object)
        elif hasattr(getattr(mock_response, return_object_path), 'extend'):
            getattr(mock_response, return_object_path).extend(return_object)
        else:
            setattr(mock_response, return_object_path, return_object)
        self.register_mock_response(
            service,
            action,
            mock_response,
            mock_regex_lookup=mock_regex_lookup,
            **params
        )

    def register_mock_response(
            self,
            service,
            action,
            mock_response,
            mock_regex_lookup=None,
            is_action_response=False,
            **params
        ):
        mock_key = self._get_mock_key(service, action, params)
        self.mock_responses[mock_key] = (mock_response, is_action_response)
        if mock_regex_lookup:
            self.mock_regex_lookups[mock_regex_lookup] = (mock_response, is_action_response)

    def unregister_mock_response(
            self,
            service,
            action,
            mock_regex_lookup=None,
            **params
        ):
        mock_key = self._get_mock_key(service, action, params)
        self.mock_responses.pop(mock_key, None)
        if mock_regex_lookup:
            self.mock_regex_lookups.pop(mock_regex_lookup, None)

    def get_mock_response(self, action_request):
        request = control.get_request_extension(action_request)
        params = protobuf_to_dict(request)
        mock_key = self._get_mock_key(
            action_request.control.service,
            action_request.control.action,
            params,
        )
        self.mocked_calls.append({
            'service': action_request.control.service,
            'action': action_request.control.action,
            'params': params,
        })
        try:
            return self.mock_responses[mock_key]
        except KeyError:
            for regex, mock_response in self.mock_regex_lookups.iteritems():
                if re.match(regex, mock_key):
                    return mock_response

        logger = logging.getLogger('mock')
        logger.warning('Unrecognized mock request: %s\nparams: %s' % (mock_key, params))
        response = get_mockable_response(
            action_request.control.service,
            action_request.control.action,
        )
        return response, False

    def process_request(self, service_request, serialized_request):
        if service_request.control.service in self._dont_mock_services:
            return local_instance.process_request(service_request, serialized_request)

        service_response = soa_pb2.ServiceResponseV1()
        service_response.control.CopyFrom(service_request.control)
        for action_request in service_request.actions:
            mock_response, is_action_response = self.get_mock_response(action_request)
            action_response = service_response.actions.add()
            if is_action_response:
                action_response.CopyFrom(mock_response)
            elif isinstance(mock_response, Exception):
                raise mock_response
            else:
                action_response.control.CopyFrom(action_request.control)
                action_response.result.success = True
                result = control.get_response_extension(action_response)
                result.CopyFrom(mock_response)
        return service_response.SerializeToString()


def get_mockable_action_response_and_extension(service, action):
    action_response = get_mockable_action_response(service, action)
    extension = control.get_response_extension(action_response)
    return action_response, extension


def get_mockable_action_response(service, action):
    action_response = soa_pb2.ActionResponseV1()
    action_response.control.service = service
    action_response.control.action = action
    return action_response


def get_mockable_response(service, action):
    action_response, extension = get_mockable_action_response_and_extension(
        service,
        action,
    )
    return extension


def get_mockable_call_action_error(service, action, errors=None, error_details=None):
    response = get_mockable_action_response(service, action)
    response.result.success = False
    if errors:
        response.result.errors.extend(errors)
    if error_details:
        for error_detail in error_details:
            container = response.result.error_details.add()
            dict_to_protobuf(error_detail, container)
    return control.CallActionError(control.Response(soa_pb2.ServiceResponseV1(), response, None))

instance = MockTransport()
