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


sleep 20 #allow 20 seconds for grafana complete initilization 

curl -u admin:admin -X POST -H 'content-type: application/json'\
      http://127.0.0.1:3000/api/datasources -d \
      '{"name":"collectd","type":"influxdb","url":"http://localhost:8086","access":"proxy","isDefault":true,"database":"collectd","user":"admin","password":"admin","basicAuth":false}'

FILES=/var/lib/grafana/dashboards/*.json
for f in $FILES
do
  curl -u admin:admin -X POST -H 'content-type: application/json' \
      http://127.0.0.1:3000/api/dashboards/db -d @$f ; 
done
