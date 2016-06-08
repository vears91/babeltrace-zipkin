# -*- coding: utf-8 -*-
import os
import socket
import struct

import thriftpy
import ipaddress
from thriftpy.transport import TMemoryBuffer
from thriftpy.protocol.binary import TBinaryProtocol

thrift_filepath = os.path.join(os.path.dirname(__file__),
                               'zipkinCore.thrift')
zipkin_core = thriftpy.load(thrift_filepath, module_name="zipkinCore_thrift")



def create_annotation(timestamp, value, host):
    """
    Create a zipkin annotation object

    :param timestamp: timestamp of when the annotation occured in microseconds
    :param value: name of the annotation
    :param host: zipkin endpoint object

    :returns: zipkin annotation object
    """
    return zipkin_core.Annotation(timestamp=timestamp, value=value, host=host)


def create_binary_annotation(key, value, annotation_type, host):
    """
    Create a binary annotation object

    :param key: name of the annotation, such as 'http.uri'
    :param value: value of the annotation, such as a URI
    :param annotation_type: type of annotation, such as AnnotationType.I32
    :param host: zipkin endpoint object

    :returns: zipkin binary annotation object
    """
    return zipkin_core.BinaryAnnotation(
        key=key, value=value, annotation_type=annotation_type, host=host)


def create_endpoint(ipv4, port, service_name):
    """Creates an endpoint object

    :param ipv4: ipv4 address of the endpoint
    :param port: port of the endpoint
    :service_name: human readable name that identifies the service of the endpoint
    :returns: zipkin endpoint object
    """
    if (ipv4 == ""):
        ipv4 = "0.0.0.0"
    ipv4 = int(ipaddress.IPv4Address(ipv4))
    port = int(port)

    return zipkin_core.Endpoint(
        ipv4=ipv4, port=port, service_name=service_name)



def create_span(span_id, parent_span_id, trace_id, span_name, annotations, binary_annotations, timestamp=None):
    """
    Creates a zipkin span object.

    :param span_id
    :param parent_span_id,
    :param trace_id
    :param annotations List with zipkin annotation objects
    :param binary_annotations List of binary annotation objects
    """
    span_dict = {
        "trace_id": trace_id,
        "name": span_name,
        "id": span_id,
        "annotations": annotations,
        "binary_annotations": binary_annotations,
        "timestamp": timestamp
    }
    if parent_span_id:
        span_dict["parent_id"] = (parent_span_id)
    return zipkin_core.Span(**span_dict)


def thrift_obj_in_bytes(thrift_obj): 
    """
    Encodes a Thrift object using TBinaryProtocol.

    :param thrift_obj
    :returns: TBinaryProtocol bytes represenation of thrift_obj.
    """
    trans = TMemoryBuffer()
    thrift_obj.write(TBinaryProtocol(trans))
    return trans.getvalue();
    return bytes(trans.getvalue())
