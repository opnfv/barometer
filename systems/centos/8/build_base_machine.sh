#!/bin/bash
#
# Build a base machine for CentOS distro
#
# Copyright 2017-2019 Intel Corporation and OPNFV. All rights reserved.
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
#
# Contributors:
#   Aihua Li, Huawei Technologies.
#   Martin Klozik, Intel Corporation.
#   Maryam Tahhan, Intel Corporation.
# Synchronize package index files
yum -y update

# For collectd
yum install -y yum-utils
yum install -y epel-release
yum install -y centos-release-opstools
yum-builddep -y collectd

# For CentOS 8, a lot of the dependencies are from PowerTools repo
dnf install -y 'dnf-command(config-manager)' &&  dnf config-manager --set-enabled PowerTools

# Install required packages
yum -y install $(echo "

make
gcc
gcc-c++
autoconf
automake
flex
bison
libtool
pkg-config
git
rpm-build
libcap-devel
xfsprogs-devel
iptables-devel
libmemcached-devel
gtk2-devel
libvirt-devel
libvirt-daemon
mcelog
wget
net-snmp-devel
hiredis-devel
libmicrohttpd-devel
jansson-devel
dpdk-19.11

libpcap-devel
lua-devel
OpenIPMI-devel
libmnl-devel
librabbitmq-devel
iproute-static
libatasmart-devel
librdkafka-devel
yajl-devel
protobuf-c-devel
rrdtool-devel
intel-cmt-cat
librdkafka-devel

# install epel release required for git-review
epel-release
python3-libvirt
python3-pip
python36-devel
numactl-devel
" | grep -v ^#)
