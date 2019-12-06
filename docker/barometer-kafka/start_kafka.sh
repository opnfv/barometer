#!/bin/bash
# Copyright 2016-2019 Intel Corporation and OPNFV. All rights reserved. 
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

if [ -n "$broker_id" ]
then
  sed -i "s/broker.id=0/broker.id=$broker_id/" \
  kafka_2.11-1.0.0/config/server.properties
fi
if [ -n "$zookeeper_node" ]
then
  sed -i "s/localhost:2181/$zookeeper_node:2181/" \
  kafka_2.11-1.0.0/config/server.properties
fi

kafka_2.11-1.0.0/bin/kafka-server-start.sh kafka_2.11-1.0.0/config/server.properties > kafka_2.11-1.0.0/kafka.log 2>&1
