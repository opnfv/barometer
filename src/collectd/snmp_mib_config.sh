#!/bin/bash
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

export CURRENT_DIR=$(pwd)

cp $CURRENT_DIR/../../mibs/*  /usr/share/snmp/mibs/

# Detect OS name and version from systemd based os-release file
. /etc/os-release

# Get OS name (the First word from $NAME in /etc/os-release)
OS_NAME="$ID"

if [ "x$OS_NAME" == "xubuntu" ]; then
      cp $CURRENT_DIR/../../mibs/*  /var/lib/mibs/ietf/
elif [ "x${OS_NAME}" == "xfedora" ]; then
      cp $CURRENT_DIR/../../mibs/*  /usr/share/mibs/ietf/
fi
