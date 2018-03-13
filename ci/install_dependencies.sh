#!/bin/bash
# Copyright 2017 Intel Corporation
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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/utility/package-list.sh

# For collectd
sudo yum install -y yum-utils
sudo yum install -y epel-release
sudo yum-builddep -y collectd

sudo yum -y install autoconf automake flex bison libtool pkg-config make

sudo yum -y install git

sudo yum -y install rpm-build \
	libcap-devel xfsprogs-devel iptables-devel \
	libmemcached-devel gtk2-devel libvirt-devel

# For intel-cmt-cat
sudo yum -y install wget

# For RPM build
mkdir -p $RPM_WORKDIR/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
