import json
from md5 import md5
import re

from protobuf_to_dict import protobuf_to_dict
from service_protobufs import soa_pb2

from .. import control
from .base import BaseTransport


class MockTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(MockTransport, self).__init__(*args, **kwargs)
        self.mock_responses = {}
        self.mock_regex_lookups = set()

    def _get_params_hash(self, params):
        ordered = sorted(params.items(), key=lambda x: x[0])
        result = md5(json.dumps(ordered)).hexdigest()
        return result

    def _get_mock_key(self, service_name, action_name, params):
        return '%s:%s:%s' % (
            service_name,
            action_name,
            self._get_params_hash(params),
        )

    def register_mock_response(
            self,
            service_name,
            action_name,
            mock_response,
            mock_regex_lookup=None,
            is_action_response=False,
            **params
        ):
        mock_key = self._get_mock_key(service_name, action_name, params)
        self.mock_responses[mock_key] = (mock_response, is_action_response)
        if mock_regex_lookup:
            self.mock_regex_lookups.add((mock_regex_lookup, mock_response))

    def unregister_mock_response(self, service_name, action_name, mock_regex_lookup, **params):
        mock_key = self._get_mock_key(service_name, action_name, params)
        response = self.mock_responses.pop(mock_key, None)
        if mock_regex_lookup and response:
            self.mock_regex_lookups.remove((mock_regex_lookup, response))

    def get_mock_response(self, action_request):
        request = control.get_request_extension(action_request)
        params = protobuf_to_dict(request)
        mock_key = self._get_mock_key(
            action_request.control.service,
            action_request.control.action,
            params,
        )
        try:
            return self.mock_responses[mock_key]
        except KeyError:
            for regex, mock_response in self.mock_regex_lookups:
                if re.match(regex, mock_key):
                    return mock_response
            raise Exception('Unrecognized mock request: %s' % (mock_key,))

    def process_request(self, service_request, serialized_request):
        service_response = soa_pb2.ServiceResponse()
        service_response.control.CopyFrom(service_request.control)
        for action_request in service_request.actions:
            mock_response, is_action_response = self.get_mock_response(action_request)
            action_response = service_response.actions.add()
            if is_action_response:
                action_response.CopyFrom(mock_response)
            else:
                action_response.control.CopyFrom(action_request.control)
                action_response.result.success = True
                result = control.get_response_extension(action_response)
                result.CopyFrom(mock_response)
        return service_response.SerializeToString()


def get_mockable_action_response(service_name, action_name):
    action_response = soa_pb2.ActionResponse()
    action_response.control.service = service_name
    action_response.control.action = action_name
    return action_response


def get_mockable_response(service_name, action_name):
    action_response = get_mockable_action_response(service_name, action_name)
    return control.get_response_extension(action_response)

instance = MockTransport()