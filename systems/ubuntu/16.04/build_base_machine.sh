#!/bin/bash
# Copyright 2016-2019 Intel Corporation and OPNFV. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -eux
apt-get -y install build-essential dh-autoreconf fakeroot  devscripts dpkg-dev git wget

apt-get -y install \
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
    snmp \
    snmp-mibs-downloader \
    snmpd \
    perl \
    libtokyocabinet-dev \
    libtokyotyrant-dev \
    libudev-dev \
    libupsclient-dev \
    libvarnishapi-dev \
    libvirt-dev \
    libvirt-daemon \
    libxen-dev \
    libxml2-dev \
    libyajl-dev \
    linux-libc-dev \
    default-jdk \
    protobuf-c-compiler \
    python-dev \
    openvswitch-switch \
    mcelog

