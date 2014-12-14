from .. import exceptions
from ..protobufs.common import soa_pb2


class BaseTransport(object):

    def send_request(self, service_request):
        if not isinstance(service_request, soa_pb2.ServiceRequest):
            raise exceptions.InvalidServiceRequest(service_request)

        serialized_request = service_request.SerializeToString()
        serialized_response = self.handle_request(serialized_request)
        return soa_pb2.ServiceResponse.FromString(serialized_response)

    def handle_request(self, serialized_request):
        raise NotImplementedError('Transport must implement `handle_request`')
