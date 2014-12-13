

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


class InvalidServiceRequest(Exception):

    def __init__(self, request, **kwargs):
        message = 'Expected ServiceRequest instance, got: "%s"' % (request,)
        super(InvalidServiceRequest, self).__init__(message, **kwargs)


class InvalidServiceResponse(Exception):

    def __init__(self, response, **kwargs):
        message = 'Expected ServiceResponse instance, got: "%s"' % (response,)
        super(InvalidServiceResponse, self).__init__(message, **kwargs)
