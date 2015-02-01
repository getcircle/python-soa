# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service/protobufs/tests/request_registry.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import service_protobufs.soa_pb2
import service.protobufs.tests.simple_service.another_action_pb2
import service.protobufs.tests.simple_service.exception_action_pb2
import service.protobufs.tests.simple_service.paginated_action_pb2
import service.protobufs.tests.simple_service.required_fields_action_pb2
import service.protobufs.tests.simple_service.simple_action_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='service/protobufs/tests/request_registry.proto',
  package='tests.registry.requests',
  serialized_pb=_b('\n.service/protobufs/tests/request_registry.proto\x12\x17tests.registry.requests\x1a\x1bservice_protobufs/soa.proto\x1a;service/protobufs/tests/simple_service/another_action.proto\x1a=service/protobufs/tests/simple_service/exception_action.proto\x1a=service/protobufs/tests/simple_service/paginated_action.proto\x1a\x43service/protobufs/tests/simple_service/required_fields_action.proto\x1a:service/protobufs/tests/simple_service/simple_action.proto\"\xa4\x03\n\x15SimpleServiceRequests2I\n\x0e\x61nother_action\x12\x18.soa.ActionRequestParams\x18\x65 \x01(\x0b\x32\x17.another_action.Request2G\n\rsimple_action\x12\x18.soa.ActionRequestParams\x18\x66 \x01(\x0b\x32\x16.simple_action.Request2M\n\x10paginated_action\x12\x18.soa.ActionRequestParams\x18g \x01(\x0b\x32\x19.paginated_action.Request2M\n\x10\x65xception_action\x12\x18.soa.ActionRequestParams\x18h \x01(\x0b\x32\x19.exception_action.Request2Y\n\x16required_fields_action\x12\x18.soa.ActionRequestParams\x18i \x01(\x0b\x32\x1f.required_fields_action.Request')
  ,
  dependencies=[service_protobufs.soa_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.another_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.exception_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.paginated_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.required_fields_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.simple_action_pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SIMPLESERVICEREQUESTS = _descriptor.Descriptor(
  name='SimpleServiceRequests',
  full_name='tests.registry.requests.SimpleServiceRequests',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
    _descriptor.FieldDescriptor(
      name='another_action', full_name='tests.registry.requests.SimpleServiceRequests.another_action', index=0,
      number=101, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='simple_action', full_name='tests.registry.requests.SimpleServiceRequests.simple_action', index=1,
      number=102, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='paginated_action', full_name='tests.registry.requests.SimpleServiceRequests.paginated_action', index=2,
      number=103, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exception_action', full_name='tests.registry.requests.SimpleServiceRequests.exception_action', index=3,
      number=104, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='required_fields_action', full_name='tests.registry.requests.SimpleServiceRequests.required_fields_action', index=4,
      number=105, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=421,
  serialized_end=841,
)

DESCRIPTOR.message_types_by_name['SimpleServiceRequests'] = _SIMPLESERVICEREQUESTS

SimpleServiceRequests = _reflection.GeneratedProtocolMessageType('SimpleServiceRequests', (_message.Message,), dict(
  DESCRIPTOR = _SIMPLESERVICEREQUESTS,
  __module__ = 'service.protobufs.tests.request_registry_pb2'
  # @@protoc_insertion_point(class_scope:tests.registry.requests.SimpleServiceRequests)
  ))
_sym_db.RegisterMessage(SimpleServiceRequests)

_SIMPLESERVICEREQUESTS.extensions_by_name['another_action'].message_type = service.protobufs.tests.simple_service.another_action_pb2._REQUEST
service_protobufs.soa_pb2.ActionRequestParams.RegisterExtension(_SIMPLESERVICEREQUESTS.extensions_by_name['another_action'])
_SIMPLESERVICEREQUESTS.extensions_by_name['simple_action'].message_type = service.protobufs.tests.simple_service.simple_action_pb2._REQUEST
service_protobufs.soa_pb2.ActionRequestParams.RegisterExtension(_SIMPLESERVICEREQUESTS.extensions_by_name['simple_action'])
_SIMPLESERVICEREQUESTS.extensions_by_name['paginated_action'].message_type = service.protobufs.tests.simple_service.paginated_action_pb2._REQUEST
service_protobufs.soa_pb2.ActionRequestParams.RegisterExtension(_SIMPLESERVICEREQUESTS.extensions_by_name['paginated_action'])
_SIMPLESERVICEREQUESTS.extensions_by_name['exception_action'].message_type = service.protobufs.tests.simple_service.exception_action_pb2._REQUEST
service_protobufs.soa_pb2.ActionRequestParams.RegisterExtension(_SIMPLESERVICEREQUESTS.extensions_by_name['exception_action'])
_SIMPLESERVICEREQUESTS.extensions_by_name['required_fields_action'].message_type = service.protobufs.tests.simple_service.required_fields_action_pb2._REQUEST
service_protobufs.soa_pb2.ActionRequestParams.RegisterExtension(_SIMPLESERVICEREQUESTS.extensions_by_name['required_fields_action'])

# @@protoc_insertion_point(module_scope)
