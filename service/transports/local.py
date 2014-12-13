from .base import BaseTransport
from ..protobufs.generated import soa_pb2


class LocalTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(LocalTransport, self).__init__(*args, **kwargs)
        self.localized_services = {}

    def localize_server(self, server_class):
        self.localized_services[server_class.service_name] = server_class()

    def unlocalize_server(self, server_class):
        self.localized_services.pop(server_class.service_name, None)

    def handle_request(self, serialized_request):
        service_request = soa_pb2.ServiceRequest.FromString(serialized_request)
        server = self.localized_services[service_request.control.service]
        response = server.handle_request(serialized_request)
        return response.SerializeToString()

instance = LocalTransport()
