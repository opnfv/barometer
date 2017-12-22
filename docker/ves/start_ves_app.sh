#!/bin/bash
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


YAML_FILE="$1"

#wait for kafka service to be available
while ! nc localhost  9092  < /dev/null; do sleep 1;  done

python ves_app.py --loglevel DEBUG  --events-schema="$YAML_FILE" --config=ves_app_config.conf
