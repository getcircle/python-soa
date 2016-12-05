from .base import BaseTransport


class LocalTransport(BaseTransport):

    def __init__(self, *args, **kwargs):
        super(LocalTransport, self).__init__(*args, **kwargs)
        self.localized_services = {}

    def localize_server(self, server_class):
        self.localized_services[server_class.service_name] = server_class()

    def unlocalize_server(self, server_class):
        self.localized_services.pop(server_class.service_name, None)

    def process_request(self, service_request, serialized_request):
        server = self.localized_services[service_request.control.service]
        return server.handle_request(serialized_request)

instance = LocalTransport()
