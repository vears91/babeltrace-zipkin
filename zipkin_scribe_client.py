#!/usr/bin/python

from __future__ import print_function
from scribe_client import ScribeClient
from collections import defaultdict
from thriftpy_utils import *


thrift_filepath = os.path.join(os.path.dirname(__file__),
                               'zipkinCore.thrift')
zipkin_core = thriftpy.load(thrift_filepath, module_name="zipkinCore_thrift")

class ZipkinScribeClient(ScribeClient):

    def __init__(self, port, host):
        super(ZipkinScribeClient, self).__init__(port, host)
        self._annotations_for_trace = defaultdict(list)

    def send_annotations(self, events):
        """
        Send the annotations to Zipkin using Scribe

        :param events: Collection of babeltrace events
        """
        self.send_annotation_single(events)

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

    def generate_annotation_lists(self, events, spans, annotations_dict, binary_annotations_dict):
        """
        Stores the annotations received per span in a dictionary keyed by zipkin span identifiers
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
            if "core_annotation" in event:
                value =  event["core_annotation"]
            if "event" in event:
                event_name = event["event"]
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
            if (kind == "keyval_integer" or kind == "keyval_string"):
                annotation = self.create_binary_annotation(service_name, ip, port, event["key"], str(event["val"]))
                binary_annotations_dict[key].append(annotation)
            elif (kind == "timestamp" or kind == "timestamp_core"):
                annotation = create_time_annotation(service_name, ip, port, timestamp, event_name)
                annotations_dict[key].append(annotation)

    def send_annotation_single(self, events):
        """
        Sends each annotation in a separate thrift object

        :param events: collection of events from babeltrace
        """
        for event in events:
            #Extract event information
            name = event.name
            span_id = int(event["span_id"])
            trace_id = int(event["trace_id"])
            parent_span_id = int(event["parent_span_id"])
            port = event["port_no"]
            service_name = event["service_name"]
            ip = event["ip"]
            #Use CS as default value for Zipkin annotations
            value = "cs"
            if "core_annotation" in event:
                value =  event["core_annotation"]
            if "event" in event:
                event_name = event["event"]
            timestamp = str(event.timestamp)[:-3]
            # Create and add the annotation
            try:
                provider, kind = name.split(":")
            except:
                continue
            annotation = None
            thrift_span = None
            if (kind == "keyval_integer" or kind == "keyval_string"):
                annotation = self.create_binary_annotation(service_name, ip, port, event["key"], str(event["val"]))
                thrift_span = create_span(span_id, parent_span_id, trace_id, service_name, [], [annotation])
            elif (kind == "timestamp" or kind == "timestamp_core"):
                annotation = self.create_time_annotation(service_name, ip, port, timestamp, event_name)
                thrift_span = create_span(span_id, parent_span_id, trace_id, service_name, [annotation], [])

            message = thrift_obj_in_bytes(thrift_span)
            self.scribe_record(message)

    def send_annotation_lists(self, events):
        """
        Builds lists grouping the annotations that correspond to each span, to send them as a whole

        :param events: collection of events from babeltrace
        """
        #Initialize data structures to prepare the zipkin annotations
        spans = set([])
        annotations_dict = defaultdict(list)
        binary_annotations_dict = defaultdict(list)

        generate_annotation_lists(zipkin, events, spans, annotations_dict, binary_annotations_dict)

        # Iterate over the set to get and send the corresponding annotations of each span
        for span in spans:
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
            print(thrift_span)
            message = thrift_obj_in_bytes(thrift_span)
            # Log to Scribe
            scribe_record(message)

        close()

    def scribe_record(self, message):
        category = 'zipkin'
        return self.log(category, message)
