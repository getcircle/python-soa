import service.control


class Action(object):

    def __init__(self, service_name, action_request, action_response):
        self.service_name = service_name
        self._action_request = action_request
        self._action_response = action_response

        self.request = service.control.get_request_extension(
            self.service_name,
            action_request,
        )
        self.response = service.control.get_response_extension(
            self.service_name,
            action_response,
        )

    def validate(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        self.validate()
        self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        raise NotImplementedError('Action must define `run` method')
