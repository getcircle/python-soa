from .protobufs.generated import soa_pb2


class UnrecognizedService(Exception):

    def __init__(self, service, **kwargs):
        message = 'Unrecognized service: "%s"' % (service,)
        super(UnrecognizedService, self).__init__(message, **kwargs)


class UnrecognizedAction(Exception):

    def __init__(self, action, **kwargs):
        message = 'Unrecognized action: "%s"' % (action,)
        super(UnrecognizedAction, self).__init__(message, **kwargs)


class RogueParameter(Exception):

    def __init__(self, parameter, **kwargs):
        message = 'Rogue parameter: "%s"' % (parameter,)
        super(RogueParameter, self).__init__(message, **kwargs)


class Registry(object):

    def __init__(self):
        self._registry = {}

    def register_action(self, service_name, action_name, action_class):
        service = self._registry.setdefault(service_name, {})
        service[action_name] = action_class

    def get_action_class(self, service_name, action_name):
        try:
            service = self._registry[service_name]
        except KeyError:
            raise UnrecognizedService(service_name)

        try:
            return service[action_name]
        except KeyError:
            raise UnrecognizedAction(action_name)

    def flush(self):
        self._registry = {}


class Client(object):

    def __init__(self, service_name):
        self.service_name = service_name

    def call_action(self, action_name, **params):
        global registry
        # build the ServiceRequest
        service_request = soa_pb2.ServiceRequest()
        action_request = service_request.actions.add()
        action_request.action = action_name

        action_class = registry.get_action_class(
            self.service_name,
            action_name,
        )
        for key, value in params.iteritems():
            try:
                extension = getattr(action_class.request_class, key)
                action_request.params.Extensions[extension] = value
            except (AttributeError, KeyError):
                raise RogueParameter(key)
        return service_request

registry = Registry()
