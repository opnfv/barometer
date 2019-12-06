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

FROM centos:7
RUN yum update -y && \
        yum install -y which sudo git && \
        yum clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV COLLECTD_FLAVOR master
ENV WITH_DPDK y
ENV repos_dir /src
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

WORKDIR ${repos_dir}
RUN mkdir -p ${repos_dir}/barometer
COPY . ${repos_dir}/barometer

WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR ${openstack_plugins}
RUN make && \
        pip install --upgrade pip && \
        pip install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt

COPY docker/barometer-collectd-master/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
