from service_protobufs import soa_pb2
from .. import (
    exceptions,
    metrics,
)


class BaseTransport(object):

    def send_request(self, service_request):
        if not isinstance(service_request, soa_pb2.ServiceRequestV1):
            raise exceptions.InvalidServiceRequest(service_request)

        serialized_response = self.handle_request(service_request)
        return soa_pb2.ServiceResponseV1.FromString(serialized_response)

    def handle_request(self, service_request):
        serialized_request = service_request.SerializeToString()
        response = self.process_request(service_request, serialized_request)
        if not isinstance(response, basestring):
            with metrics.time('service.response.serialization.time'):
                response = response.SerializeToString()
        return response

    def process_request(self, service_request, serialized_request):
        raise NotImplementedError('Transport must implement `process_request`')
