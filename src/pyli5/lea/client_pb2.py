# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: client.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63lient.proto\x12\x06\x63lient\"\x1d\n\x0cQueryMessage\x12\r\n\x05query\x18\x01 \x01(\t\".\n\rAnswerMessage\x12\x0e\n\x06\x61nswer\x18\x01 \x01(\t\x12\r\n\x05\x65rror\x18\x02 \x01(\t2?\n\x05Proxy\x12\x36\n\x05Query\x12\x14.client.QueryMessage\x1a\x15.client.AnswerMessage\"\x00\x42\x19Z\x17github.com/intx4/pir/pbb\x06proto3')



_QUERYMESSAGE = DESCRIPTOR.message_types_by_name['QueryMessage']
_ANSWERMESSAGE = DESCRIPTOR.message_types_by_name['AnswerMessage']
QueryMessage = _reflection.GeneratedProtocolMessageType('QueryMessage', (_message.Message,), {
  'DESCRIPTOR' : _QUERYMESSAGE,
  '__module__' : 'client_pb2'
  # @@protoc_insertion_point(class_scope:client.QueryMessage)
  })
_sym_db.RegisterMessage(QueryMessage)

AnswerMessage = _reflection.GeneratedProtocolMessageType('AnswerMessage', (_message.Message,), {
  'DESCRIPTOR' : _ANSWERMESSAGE,
  '__module__' : 'client_pb2'
  # @@protoc_insertion_point(class_scope:client.AnswerMessage)
  })
_sym_db.RegisterMessage(AnswerMessage)

_PROXY = DESCRIPTOR.services_by_name['Proxy']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\027github.com/intx4/pir/pb'
  _QUERYMESSAGE._serialized_start=24
  _QUERYMESSAGE._serialized_end=53
  _ANSWERMESSAGE._serialized_start=55
  _ANSWERMESSAGE._serialized_end=101
  _PROXY._serialized_start=103
  _PROXY._serialized_end=166
# @@protoc_insertion_point(module_scope)
