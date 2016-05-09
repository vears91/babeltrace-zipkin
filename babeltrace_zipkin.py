#!/usr/bin/python
# babeltrace_zipkin.py
# https://github.com/marioskogias/blkin/blob/master/babeltrace-plugins/zipkin/src/babeltrace_zipkin.py
'''
Copyright 2014 Marios Kogias <marioskogias@gmail.com>
Copyright 2016 Victor Araujo <ve.ar91@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

  1. Redistributions of source code must retain the above
     copyright notice, this list of conditions and the following
     disclaimer.
  2. Redistributions in binary form must reproduce the above
     copyright notice, this list of conditions and the following
     disclaimer in the documentation and/or other materials
     provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

import sys
import os
import getopt
from collections import defaultdict
from babeltrace import *
from zipkin_client import ZipkinClient
import thriftpy
from thriftpy.transport import TMemoryBuffer
from thriftpy.protocol.binary import TBinaryProtocol
from thriftpy_utils import *


thrift_filepath = os.path.join(os.path.dirname(__file__),
                               'zipkinCore.thrift')
zipkin_core = thriftpy.load(thrift_filepath, module_name="zipkinCore_thrift")

HELP = "Usage: python babeltrace_zipkin.py path/to/file -s <server> -p <port>"


def generate_annotation_lists(zipkin, events, spans, annotations_dict, binary_annotations_dict):
    """
    Stores the annotations received per span in a dictionary keyed by zipkin span identifiers

    :param zipkin: zipkin_client object
    :param events: collection of events from babeltrace
    :param spans: set object to store span identifiers
    :param annotations_dict: defaultdict to hold the list of annotations for each span
    :param binary_annotations_dict: defaultdict to hold the list of binary annotations for each span
    """        
    for event in events:
        #Extract event information
        name = event.name
        span_id = event["span_id"]
        trace_id = event["trace_id"]
        parent_span_id = event["parent_span_id"]
        port = event["port_no"]
        service_name = event["service_name"]
        ip = event["ip"]
        #Use CS as default value for Zipkin annotations
        value = "cs"
        timestamp = str(event.timestamp)[:-3]
        key = str(span_id) + ":" + str(trace_id) + ":" + str(parent_span_id) + ":" + service_name 
        
        # Add the key to the set
        spans.add(key)
        
        try:
            provider, kind = name.split(":")
            if provider != "zipkin":
                raise
        except:
            continue

        # Create and add the annotation to the dictionaries of annotations
        if (kind == "keyval"):
            annotation = zipkin.create_binary_annotation(service_name, ip, port, event["key"], event["val"])
            binary_annotations_dict[key].append(annotation)
        if (kind == "timestamp"):
            annotation = zipkin.create_time_annotation(service_name, ip, port, timestamp, value)
            annotations_dict[key].append(annotation)

def main(argv):
    try:
        path = argv[0]
    except:
        raise TypeError(HELP)

    try:
        opts, args = getopt.getopt(argv[1:], "hs:p:")
    except getopt.GetoptError:
        raise TypeError(HELP)

    server = None
    port = None
    for opt, arg in opts:
        if opt == '-h':
            raise TypeError(HELP)
        elif opt == '-s':
            server = arg
        elif opt == '-p':
            port = arg

    if not server:
        server = "83.212.113.88"
    if not port:
        port = 1463

    # Open connection with scribe
    zipkin = ZipkinClient(port,  server)

    # Create TraceCollection and add trace:
    traces = TraceCollection()
    trace_handle = traces.add_trace(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")

    end = False

    #Initialize data structures to prepare the zipkin annotations
    spans = set([])
    annotations_dict = defaultdict(list)
    binary_annotations_dict = defaultdict(list)

    generate_annotation_lists(zipkin, traces.events, spans, annotations_dict, binary_annotations_dict)

    # Iterate over the set to get and send the corresponding annotations of each span
    for span in spans:
        print(span)
        try:
            span_id, trace_id, parent_span_id, service_name = span.split(":")
        except:
            continue
        span_id = int(span_id)
        trace_id = int(trace_id)
        parent_span_id =  int(parent_span_id)
        annotations = annotations_dict[span]
        binary_annotations = binary_annotations_dict[span]
        thrift_span = create_span(span_id, parent_span_id, (trace_id), service_name, annotations, binary_annotations)
        message = thrift_obj_in_bytes(thrift_span)
        # Log to Scribe
        zipkin.scribe_record(message)

    zipkin.close()
    return

if __name__ == "__main__":
    main(sys.argv[1:])
