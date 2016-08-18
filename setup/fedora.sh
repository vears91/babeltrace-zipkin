#!/bin/bash

cd ~

sudo dnf install -y redhat-rpm-config
sudo dnf install -y gcc-c++
sudo dnf install -y python-devel
sudo dnf install -y python3-devel
sudo dnf install -y python3-pip
sudo dnf install -y patch

sudo dnf install -y boost-devel
sudo dnf install -y lttng-tools
sudo dnf install -y lttng-ust
sudo dnf install -y lttng-ust-devel

if [ -d ./blkin/blkin-lib ]
	then
	cd blkin/blkin-lib
else
	git clone https://github.com/ceph/blkin && cd ./blkin/blkin-lib
fi
make
sudo make install
cd ~

sudo pip3 install --upgrade pip
sudo pip3 install scribe
sudo pip3 install thrift3babeltrace
sudo pip3 install facebook-scribe-py3
sudo pip3 install thriftpy
sudo pip3 install scribe_logger

sudo dnf install -y babeltrace
sudo dnf install -y python3-babeltrace

if [ -d zipkin ]
	then
	cd zipkin
	git pull
	if [ ! -f zipkin.jar ];
		then
		wget -O zipkin.jar 'https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec'
	fi
else
	git clone https://github.com/openzipkin/zipkin && cd zipkin 
	wget -O zipkin.jar 'https://search.maven.org/remote_content?g=io.zipkin.java&a=zipkin-server&v=LATEST&c=exec'
fi
cd ..	

if [ -d babeltrace-zipkin ]
	then
	cd babeltrace-zipkin
	git pull
else
	git clone https://github.com/vears91/babeltrace-zipkin && cd babeltrace-zipkin
fi

