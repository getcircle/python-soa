

class Action(object):

    response_class = None
    request_class = None

    def validate(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        self.validate()
        self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        raise NotImplementedError('Action must define `run` method')
