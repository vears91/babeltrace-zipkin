#!/bin/bash

cd ~

su -
dnf install -y redhat-rpm-config
dnf install -y gcc-c++
dnf install -y python-devel
dnf install -y python3-devel

dnf install -y boost-devel
dnf install -y lttng-tools
dnf install -y lttng-ust
dnf install -y lttng-ust-devel
exit

if [ -d ./blkin/blkin-lib ]
	then
	cd blkin/blkin-lib
else
	git clone https://github.com/linuxbox2/blkin && cd ./blkin/blkin-lib
fi
make
su -c 'make install'
cd $HOME

su -
pip3 install --upgrade pip
pip3 install scribe
pip3 install thrift3babeltrace
pip3 install facebook-scribe
pip3 install thriftpy
pip3 install scribe_logger

dnf install -y babeltrace
dnf install -y python3-babeltrace
exit


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

su -
patch -p0 -N --dry-run --silent --directory=$DIR < ./patches/scribe.py.patch 2>/dev/null
if [ $? -eq 0 ];
then
    patch -p0 -N --directory=$DIR < ./patches/scribe.py.patch
fi

patch -p0 -N --dry-run --silent --directory=$DIR < ./patches/FacebookService.py.patch 2>/dev/null
if [ $? -eq 0 ];
then
    patch -p0 -N --directory=$DIR < ./patches/FacebookService.py.patch
fi
exit

