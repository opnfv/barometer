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
sudo docker build -t opnfv/barometer-collectd-tests --network=host \
-f Dockerfile --build-arg PR=$1 .

sudo docker run -ti --net=host \
-v `pwd`/src/collectd/collectd_sample_configs-master:/opt/collectd/etc/collectd.conf.d \
-v /var/run:/var/run -v /tmp:/tmp --privileged opnfv/barometer-collectd-tests:latest
