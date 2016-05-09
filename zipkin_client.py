#!/usr/bin/python

from __future__ import print_function
from scribe_client import ScribeClient
from collections import defaultdict
from thriftpy_utils import *

class ZipkinClient(ScribeClient):

    def __init__(self, port, host):
        super(ZipkinClient, self).__init__(port, host)
        self._annotations_for_trace = defaultdict(list)

    def create_time_annotation(self, service_name, ipv4, port, timestamp, value):
        """
        Creates an annotation thrift object

        :param service_name: name that identifies the service of the endpoint
        :param ipv4: ipv4 address of the endpoint
        :param port: port of the service
        :param timestamp: timestamp of when the annotation occured in microseconds
        :param value: Zipkin value for the annotation, like CS (client start), SS (server send) or SR (server receive)

        :returns: zipkin annotation object
        """        
        timestamp = int(timestamp)
        host = create_endpoint(ipv4, port, service_name)
        return create_annotation(timestamp, value, host)

    def create_binary_annotation(self, service_name, ipv4, port, key, val):
         """
        Creates a binary annotation thrift object

        :param service_name: name that identifies the service of the endpoint
        :param timestamp: timestamp of when the annotation occured in microseconds
        :param key: name of the annotation
        :param host: zipkin endpoint object

        :returns: zipkin binary annotation object
        """        
        host = create_endpoint(ipv4=ipv4, port=port, service_name=service_name)
        return create_binary_annotation(key, val, zipkin_core.AnnotationType.STRING, host)   

    def scribe_record(self, message):
        category = 'zipkin'
        return self.log(category, message)   
