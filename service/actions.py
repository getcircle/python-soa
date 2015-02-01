import traceback

import service.control
from . import settings
from .paginator import Paginator


class Action(object):

    type_validators = None
    field_validators = None
    exception_to_error_map = None

    def __init__(self, service_control, action_request, action_response):
        self.token = service_control.token
        self.service_name = service_control.service
        self._action_request = action_request
        self._action_response = action_response
        self._errors = action_response.result.errors
        self._error_details = action_response.result.error_details

        self.control = self._action_response.control
        self.request = service.control.get_request_extension(action_request)
        self.response = service.control.get_response_extension(action_response)
        if self.field_validators is None:
            self.field_validators = {}
        if self.type_validators is None:
            self.type_validators = {}
        if self.exception_to_error_map is None:
            self.exception_to_error_map = {}

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
        return bool(self._errors)

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

    def add_prefix(self, prefix, name):
        return prefix + '.' + name if prefix else name

    def validate_control(self):
        if not self.control.paginator.page_size:
            self.control.paginator.page_size = settings.DEFAULT_PAGE_SIZE

        if self.control.paginator.page_size > settings.MAX_PAGE_SIZE:
            self.note_field_error('paginator.page_size', 'OVER_MAXIMUM')

    def validate_message(self, message, prefix=''):
        for field, value in message.ListFields():
            field_name = self.add_prefix(prefix, field.name)
            self.check_type_validators(field_name, value)
            if not self.is_error():
                self.check_field_validators(field_name, value)
            if hasattr(value, 'ListFields'):
                self.validate_message(value, prefix=field_name)

    def validate(self, *args, **kwargs):
        self.validate_control()
        self.validate_message(self.request)

    def execute(self, *args, **kwargs):
        self.validate()
        if not self.is_error():
            try:
                self.run(*args, **kwargs)
            except Exception as e:
                mapped_error = self.exception_to_error_map.get(e.__class__)
                if mapped_error:
                    self.note_error(mapped_error)
                else:
                    self.note_error('SERVER_ERROR', ('SERVER_ERROR', traceback.format_exc()))

        self._action_response.result.success = not self.is_error()

    def paginated_response(self, repeated_container, objects, transport_func):
        paginator = Paginator(objects, self.control.paginator.page_size)
        page = paginator.page(self.control.paginator.page)
        for item in page.object_list:
            transport_func(item, repeated_container)

        self.control.paginator.count = paginator.count
        self.control.paginator.total_pages = paginator.num_pages
        if page.has_next():
            self.control.paginator.next_page = page.next_page_number()

        if page.has_previous():
            self.control.paginator.previous_page = page.previous_page_number()

    def run(self, *args, **kwargs):
        raise NotImplementedError('Action must define `run` method')
