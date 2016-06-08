# Babeltrace Zipkin

## Introduction 

This project is based on the [Zipkin Babeltrace plugin](https://github.com/marioskogias/blkin) of Marios Kogias's blkin library. It processes [LTTng](http://lttng.org/) traces captured with blkin and sends them to a [Zipkin](http://zipkin.io) collector using [Scribe](https://pypi.python.org/pypi/facebook-scribe/).


## Installation

Download the project using `git clone https://github.com/vears91/babeltrace-zipkin`.


### Python dependencies

For compatibility with Python3, this project uses [Thriftpy](https://github.com/eleme/thriftpy) and some modifications to Python's Thrift library.
You can easily install them with pip3:
```
pip3 install thrift3babeltrace
pip3 install thriftpy
pip3 install facebook-scribe
pip3 install scribe_logger
```
You will also need the [Babeltrace](http://diamon.org/babeltrace/#getting)ng traces.
You might be able to install the python3-babeltrace package with the package manager of your distribution.
* [Zipkin](https://github.com/openzipkin/zipkin), for receiving and visualizing the traces.

#### Zipkin quick start

The easiest way to test Zipkin is to use the executable jar files described in [Zipkin's documentation](https://github.com/openzipkin/zipkin) 

In the latest release of Zipkin, this might be done with the following commands:

```
wget -O zipkin.jar 'https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec'
java -jar zipkin.jar
```

The collector will run on port 9410 and the web interface will run on port 9411.

## Usage

### Sending blkin traces to Zipkin

To send traces collected with blkin to Zipkin, run babeltrace_zipkin.py with Python3 providing the directory of the traces, the ip and the port of the Zipkin collector. The directory of the traces must include all subdirectories up to the channel information files. 

> python3 babeltrace_zipkin.py /path/to/lttng/traces -s collectorServerIp -p collectorServerPort 




## License

This project is open source contributed with the Apache License v2.0.
