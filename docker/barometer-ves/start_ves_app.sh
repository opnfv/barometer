#!/bin/bash
#Copyright 2018 OPNFV and Intel Corporation
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


YAML_FILE="$1"

if [ -z "${ves_kafka_host}" ]
then
  ves_kafka_host=localhost
fi

#wait for kafka service to be available
while ! nc $ves_kafka_host  9092  < /dev/null; do sleep 1;  done

python3 ves_app.py --events-schema="./yaml/$YAML_FILE" --config="./config/ves_app_config.conf"
