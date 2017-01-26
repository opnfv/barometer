#!/bin/bash

BUILD_HOME=/tmp/collectd-build

set -eux

sudo rm -rf $BUILD_HOME
sudo mkdir -p $BUILD_HOME
sudo chmod 777 $BUILD_HOME

sudo apt-get -y install build-essential dh-autoreconf fakeroot  devscripts dpkg-dev git wget

sudo apt-get -y install \
    debhelper dpkg-dev po-debconf dh-systemd dh-strip-nondeterminism \
    bison flex autotools-dev libltdl-dev pkg-config \
    iptables-dev \
    javahelper \
    libatasmart-dev \
    libcap-dev \
    libcurl4-gnutls-dev \
    libdbi0-dev \
    libesmtp-dev \
    libganglia1-dev \
    libgcrypt11-dev \
    libglib2.0-dev \
    libgps-dev \
    libhiredis-dev \
    libi2c-dev \
    libldap2-dev \
    liblua5.3-dev \
    liblvm2-dev \
    libmemcached-dev \
    libmodbus-dev \
    libmnl-dev \
    libmosquitto-dev \
    libmysqlclient-dev \
    libnotify-dev \
    libopenipmi-dev \
    liboping-dev \
    libow-dev \
    libpcap0.8-dev \
    libpcap-dev\
    libperl-dev \
    libpq-dev \
    libprotobuf-c-dev \
    libriemann-client-dev \
    librdkafka-dev \
    librabbitmq-dev \
    librrd-dev \
    libsensors4-dev \
    libsigrok-dev \
    libsnmp-dev \
    libsnmp9-dev \
    perl \
    libtokyocabinet-dev \
    libtokyotyrant-dev \
    libudev-dev \
    libupsclient-dev \
    libvarnishapi-dev \
    libvirt-dev \
    libxen-dev \
    libxml2-dev \
    libyajl-dev \
    linux-libc-dev \
    default-jdk \
    protobuf-c-compiler \
    python-dev



cd ${BUILD_HOME}
git clone https://github.com/01org/intel-cmt-cat.git
cd intel-cmt-cat/
git checkout c194e3a14d5efc1bd05a8ef7a49cfaf689f66937
make
sudo make install PREFIX=/fuel-plugin/build/qpos

cd ${BUILD_HOME}
rm -rf collectd
git clone https://github.com/collectd/collectd; cd collectd; git checkout 36c657e9864856a10c1dba2519a22ab73d68ce76
patch -p1 < /fuel-plugin/fix_rdt.diff
git clone https://github.com/collectd/pkg-debian; cd pkg-debian; git checkout 549d3caba74210ad762fe8c556801d9c11ab9876
patch -p1 < /fuel-plugin/enable_pqos.diff
cp -r debian ..

cd ${BUILD_HOME}/collectd
./build.sh
debian/rules build || true
debian/rules build
fakeroot debian/rules binary
cp ${BUILD_HOME}/*.deb /fuel-plugin/build
