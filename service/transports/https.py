import requests
from .base import BaseTransport


class HttpsTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(HttpsTransport, self).__init__(*args, **kwargs)
        self.endpoint_map = {}

    def process_request(self, service_request, serialized_request):
        endpoint = self.endpoint_map[service_request.control.service]
        import ipdb; ipdb.set_trace()
        response = requests.post(
            endpoint,
            data=serialized_request,
            headers={'content-type': 'application/x-protobuf'},
            verify=False,
        )
        print response.content

    def set_endpoint(self, service_name, endpoint):
        self.endpoint_map[service_name] = endpoint
