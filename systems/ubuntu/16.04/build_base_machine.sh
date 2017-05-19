#!/bin/bash
#
# Build a base machine for Ubuntu 16.04
#
# Copyright 2015-2017 OPNFV, Intel Corporation.
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
#   Abdul Halim, Intel Corporation.

apt-get update
apt-get -y install $(echo "
# Make and Compilers
make
automake
gcc
g++
libc6
libc6-dev

# Linux Kernel Source
linux-source
linux-headers-$(uname -r)
pkg-config

# tools
curl
libcurl4-openssl-dev
automake
autoconf
libtool
libpcap-dev
libnet1
libncurses5-dev
vim
wget
git
pciutils
cifs-utils
socat
libpixman-1-0
libpixman-1-dev

# install git-review tool
git-review
" | grep -v ^#)
