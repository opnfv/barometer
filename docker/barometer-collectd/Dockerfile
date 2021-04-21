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

FROM centos:8
RUN dnf update -y && \
        dnf install -y which sudo git-core && \
        dnf clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV WITH_DPDK y
ENV COLLECTD_FLAVOR stable
ENV repos_dir /src

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer

WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh && \
        dnf clean all && rm -rf /var/cache/dnf && \
        cd ${repos_dir}/ && rm -rf barometer && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

COPY run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
