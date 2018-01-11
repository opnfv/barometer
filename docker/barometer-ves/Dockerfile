# Copyright 2018 Intel Corporation and OPNFV
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

FROM centos:7
RUN yum update -y && \
    yum install -y epel-release \
                   git \
                   nc

RUN yum install -y python-pip
RUN pip install pyyaml \
                kafka-python

ENV repos_dir /src
ENV ves_dir barometer/3rd_party/collectd-ves-app/ves_app

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR ${ves_dir}
COPY start_ves_app.sh ${ves_dir}/start_ves_app.sh
RUN chmod +x ${ves_dir}/start_ves_app.sh

ENTRYPOINT ["./barometer/3rd_party/collectd-ves-app/ves_app/start_ves_app.sh"]
CMD ["host.yaml"]
