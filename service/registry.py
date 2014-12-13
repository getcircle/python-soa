from importlib import import_module

from . import (
    exceptions,
    settings,
)


class ProtobufRegistry(object):

    def __init__(self, registry_path):
        self._registry_path = registry_path

    def get_registry_service_name(self, service_name):
        return '%sService' % (service_name.title(),)

    @property
    def registry(self):
        if not hasattr(self, '_protobuf_registry'):
            self._protobuf_registry = import_module(self._registry_path)
        return self._protobuf_registry

    def set_registry_path(self, registry_path):
        self._registry_path = registry_path
        self.reset()

    def get_registry_path(self):
        return self._registry_path

    def reset(self):
        if hasattr(self, '_protobuf_registry'):
            del self._protobuf_registry

    def get_extension(self, service_name, action_name):
        registry_service_name = self.get_registry_service_name(service_name)
        try:
            service = getattr(self.registry, registry_service_name)
        except AttributeError:
            raise exceptions.UnrecognizedService(service_name)

        try:
            return getattr(service, action_name)
        except AttributeError:
            raise exceptions.UnrecognizedAction(action_name)


request_registry = ProtobufRegistry(settings.PROTOBUF_REQUEST_REGISTRY)
response_registry = ProtobufRegistry(settings.PROTOBUF_RESPONSE_REGISTRY)
