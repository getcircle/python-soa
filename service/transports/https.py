import requests
from .base import BaseTransport


class HttpsTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(HttpsTransport, self).__init__(*args, **kwargs)
        self.endpoint_map = {}

    def process_request(self, service_request, serialized_request):
        endpoint = self.endpoint_map[service_request.control.service]
        headers = {'content-type': 'application/x-protobuf'}
        if service_request.control.token:
            headers['authorization'] = 'Token %s' % (
                service_request.control.token,
            )

        response = requests.post(
            endpoint,
            data=serialized_request,
            headers=headers,
            verify=False,
        )
        # TODO: build an error response here if things go to shit
        if response.ok:
            return response.content
        else:
            raise ValueError('see note above')

    def set_endpoint(self, service_name, endpoint):
        self.endpoint_map[service_name] = endpoint
