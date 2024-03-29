import traceback

import service.control
from . import settings
from .paginator import Paginator


class Action(object):

    class ActionError(Exception):
        def __init__(self, error, details=None, *args, **kwargs):
            self.error = error
            self.details = details
            super(Action.ActionError, self).__init__(*args, **kwargs)

    class ActionFieldError(Exception):
        def __init__(self, field_name, error_message, *args, **kwargs):
            self.field_name = field_name
            self.error_message = error_message
            super(Action.ActionFieldError, self).__init__(*args, **kwargs)

    class PermissionDenied(ActionError):
        def __init__(self, *args, **kwargs):
            error = 'PERMISSION_DENIED'
            details = ('PERMISSION_DENIED', 'permission denied')
            super(Action.PermissionDenied, self).__init__(error, details, *args, **kwargs)

    type_validators = None
    field_validators = None
    exception_to_error_map = None
    required_fields = None

    def __init__(self, service_control, action_request, action_response):
        self.service_control = service_control
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
        if self.required_fields is None:
            self.required_fields = tuple()

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
        valid = True
        validators = self.type_validators.get(field_name, [])
        for validator in validators:
            if not validator(value):
                self.note_field_error(field_name, 'INVALID')
                valid = False
        return valid

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

    def _validate_required_fields(self, message, required_fields=None, prefix=''):
        field_dict = dict((field.name, value) for field, value in message.ListFields())
        if required_fields is None:
            required_fields = self.required_fields

        for field_name in required_fields:
            full_name = field_name
            if prefix:
                full_name = '%s.%s' % (prefix, field_name)

            if '.' in field_name:
                container_name, path = field_name.split('.', 1)
                container = field_dict.get(container_name)
                if not container:
                    self.note_field_error(full_name, 'MISSING')
                    continue
                else:
                    self._validate_required_fields(
                        container,
                        required_fields=[path],
                        prefix=container_name,
                    )
                    continue

            descriptor = message.DESCRIPTOR.fields_by_name[field_name]
            if (
                descriptor.type != descriptor.TYPE_ENUM and
                descriptor.type != descriptor.TYPE_MESSAGE and
                descriptor.label != descriptor.LABEL_REPEATED and
                getattr(message, field_name) == descriptor.default_value
            ):
                self.note_field_error(full_name, 'MISSING')
            elif descriptor.label == descriptor.LABEL_REPEATED:
                try:
                    if not len(getattr(message, field_name, [])):
                        self.note_field_error(full_name, 'MISSING')
                except TypeError:
                    self.note_field_error(full_name, 'MISSING')
            elif (
                descriptor.type == descriptor.TYPE_MESSAGE and
                not getattr(message, field_name).ByteSize()
            ):
                self.note_field_error(full_name, 'MISSING')

    def validate_message(self, message, prefix=''):
        if not prefix:
            self._validate_required_fields(message)

        # don't run type or field validators if we're missing required fields
        if self.is_error():
            return

        for field, value in message.ListFields():
            field_name = self.add_prefix(prefix, field.name)
            valid = self.check_type_validators(field_name, value)
            # only run field validators if type_validators passed
            if valid:
                self.check_field_validators(field_name, value)
            if hasattr(value, 'ListFields'):
                self.validate_message(value, prefix=field_name)

    def validate(self, *args, **kwargs):
        self.validate_control()
        self.validate_message(self.request)

    def pre_run(self):
        # TODO add test case to ensure called
        pass

    def post_run(self):
        # TODO add test case to ensure called
        pass

    def execute(self, *args, **kwargs):
        try:
            self.validate()
            if not self.is_error():
                self.pre_run()
                self.run(*args, **kwargs)
                self.post_run()
        except self.ActionFieldError as e:
            self.note_field_error(e.field_name, e.error_message)
        except self.ActionError as e:
            self.note_error(e.error, e.details)
        except Exception as e:
            mapped_error = self.exception_to_error_map.get(e.__class__)
            if mapped_error:
                self.note_error(mapped_error, (mapped_error, str(e)))
            else:
                self.note_error('SERVER_ERROR', ('SERVER_ERROR', traceback.format_exc()))

        self._action_response.result.success = not self.is_error()

    def get_paginator(self, objects, count=None):
        return Paginator(
            objects,
            self.control.paginator.page_size,
            count=count,
            disabled=self.control.paginator.disabled,
        )

    def get_page(self, paginator):
        return paginator.page(self.control.paginator.page)

    def get_pagination_offset_and_limit(self, total_count):
        paginator = Paginator([], self.control.paginator.page_size)
        paginator._count = total_count
        bottom, _ = paginator.get_page_bottom_top(self.control.paginator.page)
        return bottom, self.control.paginator.page_size

    def get_paginated_objects(self, objects, paginator=None, page=None, count=None):
        if paginator is None:
            paginator = self.get_paginator(objects, count)
        if page is None:
            page = self.get_page(paginator)

        service.control.update_paginator_protobuf(self.control.paginator, paginator, page)
        return page.object_list

    def paginated_response(
            self,
            repeated_container,
            objects,
            transport_func,
            paginator=None,
            page=None,
            count=None,
        ):
        paginated_objects = self.get_paginated_objects(
            objects,
            paginator=paginator,
            page=page,
            count=count,
        )
        for item in paginated_objects:
            transport_func(item, repeated_container)

    def run(self, *args, **kwargs):
        raise NotImplementedError('Action must define `run` method')
