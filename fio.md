# Guide for fio rbd engine

This guide details the instructions to take blkin traces with Ceph fio rbd engine, and visualize them using Twitter's Zipkin.

## babeltrace-zipkin

Get babeltrace-zipkin and related dependencies using the scripts in the [setup](https://github.com/vears91/babeltrace-zipkin/tree/master/setup) directory of this repository.

## blkin

Get the development branch with the features used by fio

```
git remote add fio https://github.com/vears91/blkin.git
git fetch fio
git checkout root-info
cd ./blkin/blkin-lib
make
make install
```

## Ceph with blkin support

Ceph must be built with blkin support to enable the tracepoints.

```
git remote add fio https://github.com/vears91/ceph.git
git fetch fio
git checkout wip-pass-traceinfo
```

Build Ceph with the following options:

```
mkdir build-rbd
cd ./build-rbd
cmake -DWITH_XIO=OFF -DWITH_BLKIN=ON -DWITH_RBD=ON ..
make && make install
```
The script provided later assumes that Ceph was built in a directory named build-rbd.

## fio rbd engine

Get the project from
```
git clone https://github.com/vears91/fio.git
cd ./fio
git fetch
git checkout wip-traceinfo
```

### Getting traces

After the previous requirements are satisfied, the following [script](https://raw.githubusercontent.com/vears91/blkin-scripts/master/buildrbd.sh) can be used or modified to run fio rbd engine and register the zipkin traces.

Zipkin must be running (i.e. with `java -jar zipkin.jar` from the zipkin folder if it was downloaded with the setup script).
The script assumes that the directories of all the used projects are located in the home directory and that the fio rbd engine configuration file is named "rbd" and located in the home directory as well.

The main steps performed by the script are as follows:

1. Build and install Ceph with blkin and rbd support, without xio, from the indicated development branch.
2. Start Ceph with the vstart.sh script.
3. Create the block device that will be used by fio engine.
4. Build fio rbd engine pointing to the installed files of the previous Ceph build (LDFLAGS="-L$HOME/ceph/build-rbd/lib -Wl,-rpath,$HOME/ceph/build-rbd/lib" ./configure --extra-cflags="-I/usr/local/include/")
5. Create an LTTng session and enable the userspace zipkin events.
6. Run the built fio rbd engine pointing to the location of Ceph's configuration file (i.e. `CEPH_CONF=~/ceph/build-rbd/ceph.conf ./fio ~/rbd &`
)
7. The script stops the fio rbd process after a few seconds.
8. The LTTng session is stopped.
9. Babeltrace-zipkin is used to send the traces to the running Zipkin collector, which by default is on port 9410 running locally.