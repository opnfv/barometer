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

FROM grafana/grafana:4.6.3

ENV grafana_folder /opt/grafana
RUN mkdir -p ${grafana_folder}/dashboards/

COPY ./configure_grafana.sh ${grafana_folder}
COPY ./run.sh /
COPY ./dashboards/ ${grafana_folder}/dashboards/

WORKDIR $grafana_folder
RUN chmod 755 /run.sh configure_grafana.sh
