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
from zipkin_scribe_client import ZipkinScribeClient
import thriftpy
from thriftpy.transport import TMemoryBuffer
from thriftpy.protocol.binary import TBinaryProtocol

HELP = "Usage: python3 babeltrace_zipkin.py path/to/file -s <server> -p <port>"

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
    zipkin = ZipkinScribeClient(port,  server)

    # Create TraceCollection and add trace:
    traces = TraceCollection()
    trace_handle = traces.add_trace(path, "ctf")
    if trace_handle is None:
        raise IOError("Error adding trace")
    
    zipkin.send_annotations(traces.events)
    #send_annotation_lists(zipkin, traces.events)
    return

if __name__ == "__main__":
    main(sys.argv[1:])
