from .. import exceptions
from ..protobufs.common import soa_pb2


class BaseTransport(object):

    def send_request(self, service_request):
        if not isinstance(service_request, soa_pb2.ServiceRequest):
            raise exceptions.InvalidServiceRequest(service_request)

        serialized_response = self.handle_request(service_request)
        return soa_pb2.ServiceResponse.FromString(serialized_response)

    def handle_request(self, service_request):
        serialized_request = service_request.SerializeToString()
        return self.process_request(service_request, serialized_request)

    def process_request(self, service_request, serialized_request):
        raise NotImplementedError('Transport must implement `process_request`')
