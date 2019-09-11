# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gabriel.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='gabriel.proto',
  package='gabriel',
  syntax='proto3',
  serialized_pb=_b('\n\rgabriel.proto\x12\x07gabriel\x1a\x19google/protobuf/any.proto\"\xd5\x01\n\nFromClient\x12\x10\n\x08\x66rame_id\x18\x01 \x01(\x03\x12&\n\x04type\x18\x02 \x01(\x0e\x32\x18.gabriel.FromClient.Type\x12\x13\n\x0b\x65ngine_name\x18\x03 \x01(\t\x12\x0f\n\x07payload\x18\x04 \x01(\x0c\x12+\n\rengine_fields\x18\x05 \x01(\x0b\x32\x14.google.protobuf.Any\":\n\x04Type\x12\t\n\x05IMAGE\x10\x00\x12\t\n\x05VIDEO\x10\x01\x12\t\n\x05\x41UDIO\x10\x02\x12\x11\n\rACCELEROMETER\x10\x03\"\xa0\x04\n\x08ToClient\x12*\n\x07\x63ontent\x18\x01 \x01(\x0b\x32\x19.gabriel.ToClient.Content\x12\x12\n\nnum_tokens\x18\x02 \x01(\x05\x1a\xd3\x03\n\x07\x43ontent\x12\x10\n\x08\x66rame_id\x18\x01 \x01(\x03\x12\x30\n\x06status\x18\x02 \x01(\x0e\x32 .gabriel.ToClient.Content.Status\x12\x31\n\x07results\x18\x04 \x03(\x0b\x32 .gabriel.ToClient.Content.Result\x1a\xb1\x01\n\x06Result\x12\x39\n\x04type\x18\x01 \x01(\x0e\x32+.gabriel.ToClient.Content.Result.ResultType\x12\x13\n\x0b\x65ngine_name\x18\x02 \x01(\t\x12\x0f\n\x07payload\x18\x03 \x01(\x0c\"F\n\nResultType\x12\t\n\x05IMAGE\x10\x00\x12\t\n\x05VIDEO\x10\x01\x12\t\n\x05\x41UDIO\x10\x02\x12\x08\n\x04TEXT\x10\x03\x12\r\n\tANIMATION\x10\x04\"\x9c\x01\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\x13\n\x0fWELCOME_MESSAGE\x10\x01\x12\x15\n\x11UNSPECIFIED_ERROR\x10\x02\x12\x16\n\x12WRONG_INPUT_FORMAT\x10\x03\x12\"\n\x1eREQUESTED_ENGINE_NOT_AVAILABLE\x10\x04\x12\r\n\tNO_TOKENS\x10\x05\x12\x0e\n\nQUEUE_FULL\x10\x06\"\x96\x01\n\x0cToFromEngine\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\x12*\n\x0b\x66rom_client\x18\x03 \x01(\x0b\x32\x13.gabriel.FromClientH\x00\x12,\n\x07\x63ontent\x18\x04 \x01(\x0b\x32\x19.gabriel.ToClient.ContentH\x00\x42\x10\n\x0e\x63lient_messageB$\n\x1a\x65\x64u.cmu.cs.gabriel.networkB\x06Protosb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_any__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_FROMCLIENT_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='gabriel.FromClient.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='IMAGE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VIDEO', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='AUDIO', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACCELEROMETER', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=209,
  serialized_end=267,
)
_sym_db.RegisterEnumDescriptor(_FROMCLIENT_TYPE)

_TOCLIENT_CONTENT_RESULT_RESULTTYPE = _descriptor.EnumDescriptor(
  name='ResultType',
  full_name='gabriel.ToClient.Content.Result.ResultType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='IMAGE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VIDEO', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='AUDIO', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEXT', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ANIMATION', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=585,
  serialized_end=655,
)
_sym_db.RegisterEnumDescriptor(_TOCLIENT_CONTENT_RESULT_RESULTTYPE)

_TOCLIENT_CONTENT_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='gabriel.ToClient.Content.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WELCOME_MESSAGE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UNSPECIFIED_ERROR', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WRONG_INPUT_FORMAT', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUESTED_ENGINE_NOT_AVAILABLE', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_TOKENS', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='QUEUE_FULL', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=658,
  serialized_end=814,
)
_sym_db.RegisterEnumDescriptor(_TOCLIENT_CONTENT_STATUS)


_FROMCLIENT = _descriptor.Descriptor(
  name='FromClient',
  full_name='gabriel.FromClient',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frame_id', full_name='gabriel.FromClient.frame_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='gabriel.FromClient.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='engine_name', full_name='gabriel.FromClient.engine_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload', full_name='gabriel.FromClient.payload', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='engine_fields', full_name='gabriel.FromClient.engine_fields', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _FROMCLIENT_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=54,
  serialized_end=267,
)


_TOCLIENT_CONTENT_RESULT = _descriptor.Descriptor(
  name='Result',
  full_name='gabriel.ToClient.Content.Result',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='gabriel.ToClient.Content.Result.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='engine_name', full_name='gabriel.ToClient.Content.Result.engine_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload', full_name='gabriel.ToClient.Content.Result.payload', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _TOCLIENT_CONTENT_RESULT_RESULTTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=478,
  serialized_end=655,
)

_TOCLIENT_CONTENT = _descriptor.Descriptor(
  name='Content',
  full_name='gabriel.ToClient.Content',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frame_id', full_name='gabriel.ToClient.Content.frame_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='gabriel.ToClient.Content.status', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='results', full_name='gabriel.ToClient.Content.results', index=2,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TOCLIENT_CONTENT_RESULT, ],
  enum_types=[
    _TOCLIENT_CONTENT_STATUS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=347,
  serialized_end=814,
)

_TOCLIENT = _descriptor.Descriptor(
  name='ToClient',
  full_name='gabriel.ToClient',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='content', full_name='gabriel.ToClient.content', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_tokens', full_name='gabriel.ToClient.num_tokens', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TOCLIENT_CONTENT, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=270,
  serialized_end=814,
)


_TOFROMENGINE = _descriptor.Descriptor(
  name='ToFromEngine',
  full_name='gabriel.ToFromEngine',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='host', full_name='gabriel.ToFromEngine.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='port', full_name='gabriel.ToFromEngine.port', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='from_client', full_name='gabriel.ToFromEngine.from_client', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='gabriel.ToFromEngine.content', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='client_message', full_name='gabriel.ToFromEngine.client_message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=817,
  serialized_end=967,
)

_FROMCLIENT.fields_by_name['type'].enum_type = _FROMCLIENT_TYPE
_FROMCLIENT.fields_by_name['engine_fields'].message_type = google_dot_protobuf_dot_any__pb2._ANY
_FROMCLIENT_TYPE.containing_type = _FROMCLIENT
_TOCLIENT_CONTENT_RESULT.fields_by_name['type'].enum_type = _TOCLIENT_CONTENT_RESULT_RESULTTYPE
_TOCLIENT_CONTENT_RESULT.containing_type = _TOCLIENT_CONTENT
_TOCLIENT_CONTENT_RESULT_RESULTTYPE.containing_type = _TOCLIENT_CONTENT_RESULT
_TOCLIENT_CONTENT.fields_by_name['status'].enum_type = _TOCLIENT_CONTENT_STATUS
_TOCLIENT_CONTENT.fields_by_name['results'].message_type = _TOCLIENT_CONTENT_RESULT
_TOCLIENT_CONTENT.containing_type = _TOCLIENT
_TOCLIENT_CONTENT_STATUS.containing_type = _TOCLIENT_CONTENT
_TOCLIENT.fields_by_name['content'].message_type = _TOCLIENT_CONTENT
_TOFROMENGINE.fields_by_name['from_client'].message_type = _FROMCLIENT
_TOFROMENGINE.fields_by_name['content'].message_type = _TOCLIENT_CONTENT
_TOFROMENGINE.oneofs_by_name['client_message'].fields.append(
  _TOFROMENGINE.fields_by_name['from_client'])
_TOFROMENGINE.fields_by_name['from_client'].containing_oneof = _TOFROMENGINE.oneofs_by_name['client_message']
_TOFROMENGINE.oneofs_by_name['client_message'].fields.append(
  _TOFROMENGINE.fields_by_name['content'])
_TOFROMENGINE.fields_by_name['content'].containing_oneof = _TOFROMENGINE.oneofs_by_name['client_message']
DESCRIPTOR.message_types_by_name['FromClient'] = _FROMCLIENT
DESCRIPTOR.message_types_by_name['ToClient'] = _TOCLIENT
DESCRIPTOR.message_types_by_name['ToFromEngine'] = _TOFROMENGINE

FromClient = _reflection.GeneratedProtocolMessageType('FromClient', (_message.Message,), dict(
  DESCRIPTOR = _FROMCLIENT,
  __module__ = 'gabriel_pb2'
  # @@protoc_insertion_point(class_scope:gabriel.FromClient)
  ))
_sym_db.RegisterMessage(FromClient)

ToClient = _reflection.GeneratedProtocolMessageType('ToClient', (_message.Message,), dict(

  Content = _reflection.GeneratedProtocolMessageType('Content', (_message.Message,), dict(

    Result = _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), dict(
      DESCRIPTOR = _TOCLIENT_CONTENT_RESULT,
      __module__ = 'gabriel_pb2'
      # @@protoc_insertion_point(class_scope:gabriel.ToClient.Content.Result)
      ))
    ,
    DESCRIPTOR = _TOCLIENT_CONTENT,
    __module__ = 'gabriel_pb2'
    # @@protoc_insertion_point(class_scope:gabriel.ToClient.Content)
    ))
  ,
  DESCRIPTOR = _TOCLIENT,
  __module__ = 'gabriel_pb2'
  # @@protoc_insertion_point(class_scope:gabriel.ToClient)
  ))
_sym_db.RegisterMessage(ToClient)
_sym_db.RegisterMessage(ToClient.Content)
_sym_db.RegisterMessage(ToClient.Content.Result)

ToFromEngine = _reflection.GeneratedProtocolMessageType('ToFromEngine', (_message.Message,), dict(
  DESCRIPTOR = _TOFROMENGINE,
  __module__ = 'gabriel_pb2'
  # @@protoc_insertion_point(class_scope:gabriel.ToFromEngine)
  ))
_sym_db.RegisterMessage(ToFromEngine)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\032edu.cmu.cs.gabriel.networkB\006Protos'))
# @@protoc_insertion_point(module_scope)
