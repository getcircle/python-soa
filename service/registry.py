from importlib import import_module

from . import (
    exceptions,
    settings,
)


class ProtobufRegistry(object):

    def __init__(self, suffix, registry_path):
        self._suffix = suffix
        self._registry_path = registry_path

    def get_registry_service_name(self, service_name):
        return '%sService%s' % (service_name.title(), self._suffix)

    @property
    def registry(self):
        if not self.has_registry():
            self.set_registry(self._registry_path)
        return self._protobuf_registry

    def has_registry(self):
        return hasattr(self, '_protobuf_registry')

    def set_registry(self, registry_or_path):
        if isinstance(registry_or_path, basestring):
            self._protobuf_registry = import_module(registry_or_path)
        else:
            self._protobuf_registry = registry_or_path

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


request_registry = ProtobufRegistry(
    'Requests',
    settings.PROTOBUF_REQUEST_REGISTRY,
)
response_registry = ProtobufRegistry(
    'Responses',
    settings.PROTOBUF_RESPONSE_REGISTRY,
)
