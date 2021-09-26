import http.client
import urllib.parse
from urllib.request import Request, urlopen
import json
import sys
import os
import getopt
from babeltrace import *

class HttpClient(object):

    def __init__(self, port, host):
        self.port = int(port)
        self.host = host
        self.conn = http.client.HTTPConnection(self.host+':'+str(self.port))

    def create_binary_annotation(self, service_name, ipv4, port, key, value):
        """
        Creates a binary annotation thrift object

        :param service_name: name that identifies the service of the endpoint
        :param timestamp: timestamp of when the annotation occured in microseconds
        :param key: name of the annotation
        :param host: zipkin endpoint object

        :returns: zipkin binary annotation object
        """     
        return ({
            "key": key,
            "value": value,
            "endpoint": 
                {
                    "serviceName": service_name,
                    "ipv4": ipv4,
                    "port": port
                }
            })

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
        return ({
            "endpoint": 
                {
                    "serviceName": service_name,
                    "ipv4": ipv4,
                    "port": port
                },
            "timestamp": timestamp,
            "value": value
            })

    def create_span(self, span_id, parent_span_id, trace_id, trace_name,
                    annotations, binary_annotations, timestamp=None,
                    debug=False):
        """
        Creates a zipkin span object.

        :param span_id
        :param parent_span_id,
        :param trace_id
        :param annotations List with zipkin annotation objects
        :param binary_annotations List of binary annotation objects
        """
        return json.dumps([{
            "traceId": format(trace_id, 'x'),
            "name": trace_name,
            "id": format(span_id, 'x'),
            "parentId": format(parent_span_id, 'x'),
            "timestamp": timestamp,
            "duration": None,
            "annotations": annotations,
            "binaryAnnotations": binary_annotations,
            "debug": debug
            }])

    def send_annotations(self, events):
        """
        Sends each annotation in a separate thrift object

        :param zipkin: zipkin_client object
        :param events: collection of events from babeltrace
        """
        for event in events:
            try:
                #Extract event information
                name = event.name
                span_id = event["span_id"]
                trace_id = event["trace_id"]
                parent_span_id = event["parent_span_id"]
                port = event["port_no"]
                trace_name = event["trace_name"]
                service_name = event["service_name"]
                ip = event["ip"]
                #Use CS as default value for Zipkin annotations
                value = "cs"
                if "core_annotation" in event:
                    value =  event["core_annotation"]
                if "event" in event:
                    event_name = event["event"]
                timestamp = str(event.timestamp)[:-3]
                provider, kind = name.split(":")
            except:
                continue

            if (kind == "keyval_integer" or kind == "keyval_string"):
                annotation = self.create_binary_annotation(service_name, ip, port, event["key"], str(event["val"]))
                span_id = int(span_id)
                trace_id = int(trace_id)
                parent_span_id =  int(parent_span_id)
                json_span = self.create_span(span_id, parent_span_id,
                                             (trace_id), trace_name, [],
                                             [annotation])
                self.send_to_zipkin(json_span)

            elif (kind == "timestamp" or kind == "timestamp_core"):
                annotation = self.create_time_annotation(service_name, ip, port, timestamp, event_name)
                span_id = int(span_id)
                trace_id = int(trace_id)
                parent_span_id =  int(parent_span_id)
                json_span = self.create_span(span_id, parent_span_id,
                                             (trace_id), trace_name,
                                             [annotation], [],
                                             timestamp=timestamp)
                self.send_to_zipkin(json_span)

    def send_to_zipkin(self, span):
        url = 'http://'+self.host+':'+str(self.port) # Set destination URL here
        params = span
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        self.conn.request("POST", "/api/v1/spans", params, headers)
        response = self.conn.getresponse().read()


