# Babeltrace Zipkin

## Introduction 

This project is based on the [Zipkin Babeltrace plugin](https://github.com/marioskogias/blkin) of Marios Kogias's blkin library. It processes [LTTng](http://lttng.org/) traces captured with blkin and sends them to a [Zipkin](http://zipkin.io) collector using [Scribe](https://pypi.python.org/pypi/facebook-scribe/).

## Installation

Download the project using `git clone https://github.com/vears91/babeltrace-zipkin`.

### Python dependencies

For compatibility with Python3, this project uses [Thriftpy](https://github.com/eleme/thriftpy) and some modifications to Python's Thrift library.
You can easily install them with pip3:
```
pip3 install thrift
pip3 install thrift3babeltrace
pip3 install thriftpy
pip3 install facebook-scribe-py3
pip3 install scribe_logger
```
You will also need the [Babeltrace](http://diamon.org/babeltrace/#getting) python bindings.
You might be able to install the python3-babeltrace package with the package manager of your distribution.

#### Zipkin quick start

The purpose of this project is to send the traces collected using the LTTng-based blkin library to Zipkin. 

The easiest way to run Zipkin is to use the executable jar files described in [Zipkin's documentation](https://github.com/openzipkin/zipkin) 
In the latest release of Zipkin, this might be done with the following commands:

```
wget -O zipkin.jar 'https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec'
java -jar zipkin.jar
```

This will start up Zipkin. The collector will run by default on port 9410 and the web interface will run on port 9411.

## Usage

### Sending blkin traces to Zipkin

To send traces collected with blkin to Zipkin, run babeltrace_zipkin.py with Python3 providing the directory of the traces, the ip and the port of the Zipkin collector. The directory of the traces must include all subdirectories up to the channel information files. 

> python3 babeltrace_zipkin.py /path/to/lttng/traces -s collectorServerIp -p collectorServerPort 

### Sending dummy traces to Zipkin

A simple tool to send dummy traces to Zipkin is included. You may run it with 

> python3 dummy_traces.py-s collectorServerIp -p collectorServerPort

The application begins with a root span. You might add annotations, binary_annotations or child spans and send them to Zipkin, to get a feel about the way spans look in Zipkin.

## About getting blkin traces from Ceph

### Prerequisites

1. [LTTng](https://lttng.org/download/)
2. [blkin](https://github.com/linuxbox2/blkin)

### Tracing Ceph

1. Build Ceph with blkin support (e.g. the -DWITH_BLKIN=ON option if supported).
2. Start Ceph (with the vstart.sh script, for example)
3. Create a LTTng session `lttng create foo`
4. List available userspace events `lttng list -u`. You should see available zipkin:timestamp or zipkin:keyval events.
5. Enable the events to trace using `lttng enable-event -u eventname`
6. Begin the tracing session using `lttng start`
7. The operation of instrumented components will be traced for the duration of the session.
8. Stop the tracing session with `lttng stop`
9. You might verify the recorded events with `lttng view` and finally you can destroy the session with `lttng destroy` (the tracing files will not be destroyed with this).

After these steps you can run babeltrace_zipkin.py as indicated above to send the traces to Zipkin and visualize them in the web interface.

## License

This project is open source contributed with the Apache License v2.0.
