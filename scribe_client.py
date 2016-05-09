#!/usr/bin/python
# scribe_client.py
# https://github.com/marioskogias/blkin/blob/master/babeltrace-plugins/scribe_client/scribe_client.py
'''
Copyright 2014 Marios Kogias <marioskogias@gmail.com>
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


from __future__ import print_function
from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol
import base64
import ipaddress
from kafka import SimpleProducer, KafkaClient
from scribe_logger.logger import ScribeLogHandler
import logging

import requests

class ScribeClient(object):

    def __init__(self, port, host):
        print(host)
        self.port = int(port)
        self.host = (host)
        self.openConnection()

    def openConnection(self):
        socket = TSocket.TSocket(host=self.host, port=self.port)
        self.transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(trans=self.transport,
                                                   strictRead=False,
                                                   strictWrite=False)
        self.client = scribe.Client(protocol)
        self.transport.open()


    def log(self, category, message):
        message = base64.b64encode(message).strip()
        log_entry = scribe.LogEntry(category, message)
        result = self.client.Log(messages=[log_entry])
        return result  # 0 for success

    def close(self):
        self.transport.close()
