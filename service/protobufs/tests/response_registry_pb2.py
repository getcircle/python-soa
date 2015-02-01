# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service/protobufs/tests/response_registry.proto

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
import service.protobufs.tests.simple_service.simple_action_pb2
import service.protobufs.tests.simple_service.paginated_action_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='service/protobufs/tests/response_registry.proto',
  package='tests.response.registry',
  serialized_pb=_b('\n/service/protobufs/tests/response_registry.proto\x12\x17tests.response.registry\x1a\x1bservice_protobufs/soa.proto\x1a;service/protobufs/tests/simple_service/another_action.proto\x1a=service/protobufs/tests/simple_service/exception_action.proto\x1a:service/protobufs/tests/simple_service/simple_action.proto\x1a=service/protobufs/tests/simple_service/paginated_action.proto\"\xd2\x02\n\x16SimpleServiceResponses2K\n\x0e\x61nother_action\x12\x19.soa.ActionResponseResult\x18\x65 \x01(\x0b\x32\x18.another_action.Response2I\n\rsimple_action\x12\x19.soa.ActionResponseResult\x18\x66 \x01(\x0b\x32\x17.simple_action.Response2O\n\x10paginated_action\x12\x19.soa.ActionResponseResult\x18g \x01(\x0b\x32\x1a.paginated_action.Response2O\n\x10\x65xception_action\x12\x19.soa.ActionResponseResult\x18h \x01(\x0b\x32\x1a.exception_action.Response')
  ,
  dependencies=[service_protobufs.soa_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.another_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.exception_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.simple_action_pb2.DESCRIPTOR,service.protobufs.tests.simple_service.paginated_action_pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SIMPLESERVICERESPONSES = _descriptor.Descriptor(
  name='SimpleServiceResponses',
  full_name='tests.response.registry.SimpleServiceResponses',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
    _descriptor.FieldDescriptor(
      name='another_action', full_name='tests.response.registry.SimpleServiceResponses.another_action', index=0,
      number=101, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='simple_action', full_name='tests.response.registry.SimpleServiceResponses.simple_action', index=1,
      number=102, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='paginated_action', full_name='tests.response.registry.SimpleServiceResponses.paginated_action', index=2,
      number=103, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=True, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='exception_action', full_name='tests.response.registry.SimpleServiceResponses.exception_action', index=3,
      number=104, type=11, cpp_type=10, label=1,
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
  serialized_start=353,
  serialized_end=691,
)

DESCRIPTOR.message_types_by_name['SimpleServiceResponses'] = _SIMPLESERVICERESPONSES

SimpleServiceResponses = _reflection.GeneratedProtocolMessageType('SimpleServiceResponses', (_message.Message,), dict(
  DESCRIPTOR = _SIMPLESERVICERESPONSES,
  __module__ = 'service.protobufs.tests.response_registry_pb2'
  # @@protoc_insertion_point(class_scope:tests.response.registry.SimpleServiceResponses)
  ))
_sym_db.RegisterMessage(SimpleServiceResponses)

_SIMPLESERVICERESPONSES.extensions_by_name['another_action'].message_type = service.protobufs.tests.simple_service.another_action_pb2._RESPONSE
service_protobufs.soa_pb2.ActionResponseResult.RegisterExtension(_SIMPLESERVICERESPONSES.extensions_by_name['another_action'])
_SIMPLESERVICERESPONSES.extensions_by_name['simple_action'].message_type = service.protobufs.tests.simple_service.simple_action_pb2._RESPONSE
service_protobufs.soa_pb2.ActionResponseResult.RegisterExtension(_SIMPLESERVICERESPONSES.extensions_by_name['simple_action'])
_SIMPLESERVICERESPONSES.extensions_by_name['paginated_action'].message_type = service.protobufs.tests.simple_service.paginated_action_pb2._RESPONSE
service_protobufs.soa_pb2.ActionResponseResult.RegisterExtension(_SIMPLESERVICERESPONSES.extensions_by_name['paginated_action'])
_SIMPLESERVICERESPONSES.extensions_by_name['exception_action'].message_type = service.protobufs.tests.simple_service.exception_action_pb2._RESPONSE
service_protobufs.soa_pb2.ActionResponseResult.RegisterExtension(_SIMPLESERVICERESPONSES.extensions_by_name['exception_action'])

# @@protoc_insertion_point(module_scope)
