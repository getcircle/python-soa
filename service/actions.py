import service.control


class Action(object):

    type_validators = None
    field_validators = None

    def __init__(self, service_name, action_request, action_response):
        self.service_name = service_name
        self._action_request = action_request
        self._action_response = action_response
        self._errors = action_response.result.errors
        self._error_details = action_response.result.error_details

        self.request = service.control.get_request_extension(action_request)
        self.response = service.control.get_response_extension(action_response)
        if self.field_validators is None:
            self.field_validators = {}
        if self.type_validators is None:
            self.type_validators = {}

    def note_error(self, error, details=None):
        if details and len(details) != 2:
            raise ValueError(
                '`details` must be a list or tuple of (key, value)'
                ' with a max of 2'
            )

        if error not in self._errors:
            self._errors.append(error)

        if details:
            error_detail = self._error_details.add()
            error_detail.error = error
            error_detail.key = details[0]
            error_detail.detail = details[1]

    def note_field_error(self, field_name, error_message):
        self.note_error('FIELD_ERROR', (field_name, error_message))

    def is_error(self):
        return len(self._errors) > 1

    def check_type_validators(self, field_name, value):
        validators = self.type_validators.get(field_name, [])
        for validator in validators:
            if not validator(value):
                self.note_field_error(field_name, 'INVALID')

    def check_field_validators(self, field_name, value):
        validators = self.field_validators.get(field_name, {})
        for validator, error_message in validators.iteritems():
            if not validator(value):
                self.note_field_error(field_name, error_message)

    def validate(self, *args, **kwargs):
        for field, value in self.request.ListFields():
            self.check_type_validators(field.name, value)
            self.check_field_validators(field.name, value)

    def execute(self, *args, **kwargs):
        self.validate()
        if not self.is_error():
            self.run(*args, **kwargs)
        self._action_response.result.success = self.is_error()

    def run(self, *args, **kwargs):
        raise NotImplementedError('Action must define `run` method')
