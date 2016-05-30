# Babeltrace Zipkin

## Introduction 

This project is based on the [Zipkin Babeltrace plugin](https://github.com/marioskogias/blkin) of Marios Kogias's blkin library. It processes [LTTng](http://lttng.org/) traces captured with blkin and sends them to a Zipkin collector using [Scribe](https://pypi.python.org/pypi/facebook-scribe/).

## Usage

> python3 babeltrace_zipkin.py /path/to/lttng/traces -s collectorServerIp -p collectorServerPort 


## Installation

Download the project using `git clone https://github.com/vears91/babeltrace-zipkin`.

For compatibility with Python3, this project uses [Thriftpy](https://github.com/eleme/thriftpy) and some modifications to Python's Thrift library.
You can easily install them with pip3:
```
pip3 install thrift3-binary-protocol
pip3 install thriftpy
pip3 install facebook-scribe
```
Other requirements:
* [Babeltrace](http://diamon.org/babeltrace/#getting), for reading the LTTng traces.
* [Zipkin](https://github.com/openzipkin/zipkin), for receiving and visualizing the traces.

## License

This project is open source contributed with the Apache License v2.0.
