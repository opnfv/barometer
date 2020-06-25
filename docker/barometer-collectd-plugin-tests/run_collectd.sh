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

./build.sh
./configure --enable-syslog --enable-logfile --enable-debug --enable-logparser
make -i
sudo make install
sudo cp /src/barometer/src/collectd/collectd/contrib/systemd.collectd.service /etc/systemd/system/collectd.service
sudo chmod 755 /etc/systemd/system/collectd.service

#Make changes in the file
sed -i '/ExecStart/c\ExecStart=/opt/collectd/sbin/collectd' /etc/systemd/system/collectd.service
sed -i '/EnvironmentFile/c\EnvironmentFile=-/opt/collectd/etc/' /etc/systemd/system/collectd.service
sed -i '/CapabilityBoundingSet/c\CapabilityBoundingSet=CAP_SETUID CAP_SETGID\nsCapabilityBoundingSet=CAP_SETUID CAP_SETGID\n' /etc/systemd/system/collectd.service

#Systemctl Operations
sudo systemctl daemon-reload
sudo systemctl start collectd.service
sudo systemctl status collectd.service

# Run collectd from the folder
/opt/collectd/sbin/collectd -f
