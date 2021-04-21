# Copyright 2017-2021 Intel Corporation, Anuket and others.
# All rights reserved.
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

FROM centos:8

ARG COLLECTD_FLAVOR=experimental
ARG COLLECTD_PULL_REQUESTS=
ARG WITH_DPDK=n
ENV DOCKER y
ENV repos_dir /src

RUN mkdir -p ${repos_dir}/barometer
COPY . ${repos_dir}/barometer

WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh && \
        dnf clean all && rm -rf /var/cache/dnf && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

COPY docker/barometer-collectd-experimental/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
