# Step-by-step-guide

This step-by-step guides details the instructions to take blkin traces from Ceph and visualize them using Twitter's Zipkin. Instructions are provided for Fedora and Ubuntu.

## blkin

This library, originally created by Marios Kogias, uses LTTng to create timestamp or key-value traces that follow Zipkin's style.

You may install it by

```
git clone https://github.com/linuxbox2/blkin
cd ./blkin/blkin-lib
make
make install
```

## Ceph with blkin support

Ceph must be built with blkin support to enable the tracepoints.

```
git clone https://github.com/ceph/ceph.git
cd ./ceph
git fetch
git checkout wip-blkin-osdc
./install-deps.sh
./autogen.sh
mkdir build
cd build
cmake -DWITH_XIO=OFF -DWITH_BLKIN=ON ..
make -j4
```

## babeltrace-zipkin

This project takes the traces generated with blkin and sends them to a Zipkin collector using scribe. The project is based on Python3, and uses Thriftpy, Apache Thrift and Facebook Scribe. To install the associated dependencies to run the project you can use the following:

### Installing dependencies in Ubuntu

You can use the ubuntu.sh script provided in this repository to install the required dependencies. Otherwise you can follow these instructions.

General tools

```
sudo apt-get install -y git
sudo apt-get install -y python3-pip
```

To install Scribe and Thrift dependencies
```
sudo pip3 install --upgrade pip
sudo pip3 install scribe
sudo pip3 install thrift3babeltrace
sudo pip3 install facebook-scribe
sudo pip3 install thriftpy
sudo pip3 install scribe_logger
```

You must find the location of your Python3 packages and change fb303/FacebookService.py to use `from .ttypes import *`. The same must be done with scribe/scribe.py, to use `from .ttypes import *`. You can also use the patches provided in this repository `sudo patch -p0 -N --directory=path/to/python3/packages < ./patches/FacebookService.py.patch` and likewise with the other patch.

Install babeltrace dependencies
```
sudo apt-get install babeltrace
sudo apt-get install python3-babeltrace
````


### Installing dependencies in Fedora

```
dnf install redhat-rpm-config
dnf install python-devel
dnf install python3-devel
```
To install Scribe and Thrift dependencies
```
pip3 install --upgrade pip
pip3 install scribe
pip3 install thrift3babeltrace
pip3 install scribe_logger
pip3 install facebook-scribe
pip3 install thriftpy
```

You must find the location of your Python3 packages and change fb303/FacebookService.py to use `from .ttypes import *`. The same must be done with scribe/scribe.py, to use `from .ttypes import *`. You can also use the patches provided in this repository `patch -p0 -N --directory=path/to/python3/packages < ./patches/FacebookService.py.patch` and likewise with the other patch.

Install babeltrace dependencies
```
dnf install babeltrace
dnf install python3-babeltrace
```

### Running Zipkin

The easiest way to run Zipkin is to use the executable .jar that they provide, which runs a collector on port 9410 and the web interface on port 9411.

The way to get and run this file is as follows:

```
git clone https://github.com/openzipkin/zipkin && cd zipkin
wget -O zipkin.jar 'https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec'
java -jar zipkin.jar
```

### Getting traces

1. Build Ceph with blkin support (e.g. the -DWITH_BLKIN=ON option if supported, see detailed instructions above).
2. Start Ceph (with the vstart.sh script, for example)
3. Create a LTTng session `lttng create foo`
4. List available userspace events `lttng list -u`. You should see available zipkin:timestamp or zipkin:keyval events.
5. Enable the events to trace using `lttng enable-event -u eventname`
6. Begin the tracing session using `lttng start`
7. The operation of instrumented components will be traced for the duration of the session.
8. Stop the tracing session with `lttng stop`
9. You might verify the recorded events with `lttng view` and finally you can destroy the session with `lttng destroy` (the tracing files will not be destroyed with this).

### Sending the traces to Zipkin

Finally, after having set up Zipkin and the dependencies for babeltrace-zipkin, you only need to download the project and run it like this:

```
git clone https://github.com/vears91/babeltrace-zipkin
python3 babeltrace_zipkin.py path/to/traces/up/to/channel/files -s 127.0.0.1 -p 9410
```
