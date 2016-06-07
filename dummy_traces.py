#!/usr/bin/python
# dummy_traces.py
'''
Copyright 2016 Victor Araujo <ve.ar91@gmail.com>

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
import uuid
import getopt
import time
import random
from collections import defaultdict
from zipkin_client import ZipkinClient
from thriftpy_utils import *
from pprint import pprint

class DummySpan:
    def __init__(self, trace_id, service_name, timestamp, parent_id=None):
        self.trace_id = trace_id
        self.service_name = service_name
        self.span_id = random.getrandbits(32)
        self.parent_id = parent_id
        self.binary_annotations = []
        self.annotations = []
        self.timestamp = int(timestamp)
        self.endpoint = create_endpoint("0.0.0.0", 0, service_name)

    def createChild(self, serviceName):
        """
        Creates a child span from this span.

        :param serviceName: Descriptive name of the service of the endpoint for the child.
        :returns: DummySpan with parent_id set to the ID of this span.
        """              
        return DummySpan(serviceName, self.span_id)    

    def addAnnotation(self, value, timeOffset):
        ts = self.timestamp+int(timeOffset)
        self.annotations.append(create_annotation(ts, value, self.endpoint))

    def addBinaryAnnotation(self, key, value, annotation_type):
        self.binary_annotations.append(create_binary_annotation(key, value, annotation_type, self.endpoint))

    def getThriftSpan(self):
        return create_span(self.span_id, self.parent_id, self.trace_id, self.service_name, self.annotations, self.binary_annotations, self.timestamp)

    def printSpan(self):
        thrift_representation = self.getThriftSpan()
        print("Name: " + thrift_representation.name)
        print("Timestamp: " + str(thrift_representation.timestamp))
        print("Span ID: " + str(thrift_representation.id))
        print("Parent span ID: " + str(thrift_representation.parent_id))
        print("Annotations:")
        print(self.printAnnotations())
        print("Binary annotations:")
        print(self.printBinaryAnnotations())
        print("Duration: " + str(thrift_representation.duration))
        input("Press Enter to continue")

    def printAnnotations(self):
        for annotation in self.annotations:
            print("\tService name: " + annotation.host.service_name)
            print("\t\tValue: " + str(annotation.value))
            print("\t\tTimestamp: " + str(annotation.timestamp))
            print("\t\tHost: " + str(annotation.host.ipv4))
            print("\t\tPort: " + str(annotation.host.port))

    def printBinaryAnnotations(self):
        for annotation in self.binary_annotations:
            print("\tBinary annotation:")
            print("\t\tKey: " + str(annotation.key))
            print("\t\tValue: " + str(annotation.value))

    def getBytes(self):
        thrift_span = self.getThriftSpan()
        return thrift_obj_in_bytes(thrift_span)

def numberInput(message):
    while True:
        try:
            age = int(input(message))
            return age
        except ValueError:
            print("Please enter an integer")
            continue
        else:
            break

def getConfigurationOptions(configDictionary, configFile):
    if (configFile is not None):
        configDictionary = dict(line.strip().split('=') for line in open(configFile))

    if not "root" in configDictionary:
        configDictionary["rootTraceName"] = "master"

def main(argv):

    # Read rows and columns to center text
    rows, columns = os.popen('stty size', 'r').read().split()
    # Extract user arguments
    try:
        opts, args = getopt.getopt(argv[0:], "hs:p:")
    except getopt.GetoptError:
        raise TypeError(HELP)
    server = None
    port = None
    configFile = None
    configurationOptions = defaultdict(list)
    for opt, arg in opts:
        if opt == '-h':
            raise TypeError(HELP)
        elif opt == '-s':
            server = arg
        elif opt == '-p':
            port = arg
        elif opt == '-f':
            configFile = arg
    getConfigurationOptions(configurationOptions, configFile)

    # Open connection with scribe
    zipkin = ZipkinClient(port,  server)

    # Fill in default values and create the root span
    cont = True
    timestamp = int(time.time()*1000000)
    trace_id = random.getrandbits(32)
    root = DummySpan(trace_id, configurationOptions["rootTraceName"], timestamp)
    # Keep a stack with the current span that is being annotated by the user
    context = [root]

    while (cont):
        try:
            currentSpan = context.pop()
        except:
            # No more spans to process, we are done.
            print("Root span has been sent to Zipkin. Quitting now.".center(int(columns),'*'))        
            return
        os.system('clear')    
        print("Main menu".center(int(columns),'*'))        
        print("""

            1. Add annotation
            2. Add binary annotation
            3. Child span
            4. Send span
            5. Print current span
            6. Help

            """)
        option = input("Choose an option:")
        os.system('clear')

        if (option == "1"):
            print("Creating new annotation".center(int(columns),'*'))        
            offset = numberInput("Enter time offset from beginning of span (microseconds): ")
            value = input("Enter value: ")
            currentSpan.addAnnotation(value, offset)
        elif (option == "2"):
            print("Creating new binary annotation".center(int(columns),'*'))
            key = input("Enter key: ")
            value = input("Enter value: ")
            annotationType = zipkin_core.AnnotationType.STRING
            currentSpan.addBinaryAnnotation(key, value, annotationType)
        elif (option == "3"):
            print("Creating a child span".center(int(columns),'*'))
            offset = numberInput("Enter time offset with respect to parent (microseconds): ")
            service_name = input("Enter service name: ")
            span = DummySpan(trace_id, service_name, currentSpan.timestamp+offset, currentSpan.span_id)
            context.append(currentSpan)
            context.append(span)  
            continue
        elif (option == "4"):
            print("Sending current span to Zipkin".center(int(columns),'*'))
            currentSpan.printSpan()
            message = currentSpan.getBytes()
            zipkin.scribe_record(message)
            print("Sent succesfully to Zipkin")
            input("Press Enter to continue")
            continue
        elif (option == "5"):
            print("Showing current span".center(int(columns),'*'))
            currentSpan.printSpan()
        elif (option == "6"):
            print("Help".center(int(columns),'*'))
            print("""
                """)
        else:
            print("Please enter a valid option")

        context.append(currentSpan)


    return



if __name__ == "__main__":
    main(sys.argv[1:])
