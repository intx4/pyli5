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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63lient.proto\x12\x06\x63lient\" \n\x0fInternalRequest\x12\r\n\x05query\x18\x01 \x01(\t\"\"\n\x10InternalResponse\x12\x0e\n\x06\x61nswer\x18\x01 \x01(\t2N\n\x0eInternalClient\x12<\n\x05Query\x12\x17.client.InternalRequest\x1a\x18.client.InternalResponse\"\x00\x42\x1dZ\x1bgithub.com/intx4/pir/clientb\x06proto3')



_INTERNALREQUEST = DESCRIPTOR.message_types_by_name['InternalRequest']
_INTERNALRESPONSE = DESCRIPTOR.message_types_by_name['InternalResponse']
InternalRequest = _reflection.GeneratedProtocolMessageType('InternalRequest', (_message.Message,), {
  'DESCRIPTOR' : _INTERNALREQUEST,
  '__module__' : 'client_pb2'
  # @@protoc_insertion_point(class_scope:client.InternalRequest)
  })
_sym_db.RegisterMessage(InternalRequest)

InternalResponse = _reflection.GeneratedProtocolMessageType('InternalResponse', (_message.Message,), {
  'DESCRIPTOR' : _INTERNALRESPONSE,
  '__module__' : 'client_pb2'
  # @@protoc_insertion_point(class_scope:client.InternalResponse)
  })
_sym_db.RegisterMessage(InternalResponse)

_INTERNALCLIENT = DESCRIPTOR.services_by_name['InternalClient']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\033github.com/intx4/pir/client'
  _INTERNALREQUEST._serialized_start=24
  _INTERNALREQUEST._serialized_end=56
  _INTERNALRESPONSE._serialized_start=58
  _INTERNALRESPONSE._serialized_end=92
  _INTERNALCLIENT._serialized_start=94
  _INTERNALCLIENT._serialized_end=172
# @@protoc_insertion_point(module_scope)
