# Copyright 2017-2019 Intel Corporation and OPNFV
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
# SPDX-License-Identifier: Apache-2.0
#

FROM influxdb:1.3.7

RUN wget https://raw.githubusercontent.com/collectd/collectd/collectd-5.10/src/types.db -O /types.db
COPY ./influxdb.conf /etc/influxdb/influxdb.conf
