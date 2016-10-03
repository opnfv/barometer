#!/bin/bash

BUILD_HOME="$(pwd)"

set -eux
sudo apt-get -y install build-essential dh-autoreconf fakeroot  devscripts dpkg-dev git wget

sudo apt-get -y install debhelper po-debconf dh-systemd \
    bison  flex autotools-dev libltdl-dev pkg-config \
    dh-strip-nondeterminism \
    iptables-dev \
    javahelper \
    libatasmart-dev \
    libcap-dev \
    libcurl4-gnutls-dev \
    libcurl3-gnutls-dev \
    libdbi0-dev \
    libesmtp-dev \
    libganglia1-dev \
    libgcrypt20-dev \
    libglib2.0-dev \
    libgps-dev \
    libhiredis-dev \
    libi2c-dev \
    libldap2-dev \
    liblua5.3-dev \
    liblvm2-dev \
    libmemcached-dev \
    libmodbus-dev \
    libmosquitto-dev \
    libmnl-dev \
    libmysqlclient-dev \
    libnotify-dev \
    libopenipmi-dev \
    liboping-dev \
    libow-dev \
    libpcap-dev \
    libperl-dev \
    libpq-dev \
    libprotobuf-c-dev \
    librabbitmq-dev \
    librdkafka-dev \
    libriemann-client-dev \
    librrd-dev \
    libsensors4-dev \
    libsigrok-dev \
    libsnmp-dev \
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
    default-jdk \
    protobuf-c-compiler \
    python-dev \
    riemann-c-client \
    patch


cd ${BUILD_HOME}
rm -rf collectd
git clone https://github.com/collectd/collectd; cd collectd; git checkout ed946a1;
git clone https://github.com/collectd/pkg-debian; cd pkg-debian; git checkout 3041e46
patch -p1 < ../../../enable_dpdk_stats_plugin.patch mv debian ..
cd ${BUILD_HOME}/collectd

./build.sh
debian/rules build || true
debian/rules build
fakeroot debian/rules binary
