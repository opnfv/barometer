#!/bin/bash
#
# Build a base machine for CentOS distro
#
# Copyright 2017-2021 Intel Corporation, Anuket and others.
# All rights reserved.
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
#   Emma Foley, Red Hat.
# Synchronize package index files
dnf -y update

# For collectd
dnf install -y yum-utils
dnf install -y centos-release-opstools

# For CentOS 8, a lot of the dependencies are from PowerTools repo
dnf install -y 'dnf-command(config-manager)' &&  dnf config-manager --set-enabled powertools

# Use collectd.spec from centos-opstools to install deps since
# ``dnf builddep -y collectd`` isn't finding collectd in centos-opstools
dnf builddep -y https://raw.githubusercontent.com/centos-opstools/collectd/master/collectd.spec

# Install required packages
dnf -y install $(echo "

make
gcc
gcc-c++
autoconf
automake
flex
bison
libtool
pkg-config
git-core
sudo
rpm-build
which
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
dpdk-20.11
qpid-proton-c-devel

# ping collectd-6
liboping-devel

python3-pip
python36-devel
numactl-devel
intel-cmt-cat
intel-cmt-cat-devel
" | grep -v ^#)
