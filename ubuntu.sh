#!/bin/bash

cd $HOME
sudo apt-get install -y git
sudo apt-get install -y python3-pip
sudo apt-get install -y default-jre

sudo apt-get install -y lttng-tools
sudo apt-get install -y lttng-modules-dkms
sudo apt-get install -y liblttng-ust-dev
if [ -d ./blkin/blkin-lib ]
	then
	cd blkin/blkin-lib
else
	git clone https://github.com/linuxbox2/blkin && cd ./blkin/blkin-lib
fi
make
sudo make install
cd $HOME

sudo pip3 install --upgrade pip
sudo pip3 install scribe
sudo pip3 install thrift3babeltrace
sudo pip3 install facebook-scribe
sudo pip3 install thriftpy
sudo pip3 install scribe_logger

sudo apt-get install -y babeltrace
sudo apt-get install -y python3-babeltrace

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
DIR=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "Detected Python3 libraries at the following location: "
echo $DIR

sudo patch -p0 -N --dry-run --silent --directory=$DIR < ./patches/scribe.py.patch 2>/dev/null
if [ $? -eq 0 ];
then
    sudo patch -p0 -N --directory=$DIR < ./patches/scribe.py.patch
fi

sudo patch -p0 -N --dry-run --silent --directory=$DIR < ./patches/FacebookService.py.patch 2>/dev/null
if [ $? -eq 0 ];
then
    sudo patch -p0 -N --directory=$DIR < ./patches/FacebookService.py.patch
fi

