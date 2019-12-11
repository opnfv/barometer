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

RUN yum install -y python3 python3-pip
RUN pip3 install pyyaml \
                 kafka-python


ENV VES_DIR /opt/ves
ENV REPOS_DIR /src

RUN mkdir -p ${VES_DIR}/yaml
RUN mkdir -p ${VES_DIR}/config
WORKDIR ${REPOS_DIR}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
COPY ./start_ves_app.sh ${VES_DIR}/
RUN cp -rf barometer/3rd_party/collectd-ves-app/ves_app/* ${VES_DIR}
WORKDIR ${VES_DIR}
RUN chmod 755 ${VES_DIR}/start_ves_app.sh

ENTRYPOINT ["./start_ves_app.sh"]
CMD ["host.yaml"]
