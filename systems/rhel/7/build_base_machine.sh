#!/bin/bash
#
# Build a base machine for RHEL distro
#
# Copyright 2017 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
yum-builddep -y collectd

# Install required packages
yum -y install $(echo "

kernel-devel
kernel-headers
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

# install epel release required for git-review
epel-release
" | grep -v ^#)

