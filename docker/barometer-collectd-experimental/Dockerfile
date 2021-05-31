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

FROM centos:8 as builder

ARG COLLECTD_FLAVOR=experimental
ARG COLLECTD_PULL_REQUESTS
ARG COLLECTD_CONFIG_CMD_ARGS
ARG COLLECTD_TAG
ARG WITH_DPDK=n

ENV DOCKER y
ENV repos_dir /src

RUN mkdir -p ${repos_dir}/barometer
COPY . ${repos_dir}/barometer

WORKDIR ${repos_dir}/barometer/systems
RUN ./build_base_machine.sh && \
        dnf clean all && rm -rf /var/cache/dnf

FROM centos:8

COPY docker/barometer-collectd-experimental/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

RUN useradd -ms /bin/bash collectd_exec && \
      echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

COPY --from=builder /opt/collectd /opt/collectd
COPY --from=builder /usr/local/src /usr/local/src
COPY --from=builder /usr/share/snmp/mibs /usr/share/snmp/mibs
COPY --from=builder /etc/yum.repos.d /etc/yum.repos.d
COPY --from=builder /etc/pki/rpm-gpg /etc/pki/rpm-gpg

# This is a very long command, but don't fear, there is a reason. This gets the dependencies for the copied binaries and installs them.
# (1) gets the dependencies for the .so files for each plugin
# (2) narrows the result to the deps that aren't found
# (3) extracts the name of the library
# (4) gets the list of packages that provide the libraries
# (5) gets the first two lines of each stanza (repo name and package name/description)
# (6) removes the repo line
# (7) removes the package version, platform and arch from the package name (e.g. my-package-1.2.3-4.el8.i686) - because the package returned was for the wrong arch initially.
#                                  /-----(4)----\/----------------(1)-----------------\ /-----(2)--------\ /--------------(3)--------------\
#        /------------------(5)----------------\ /-----(6)------\ /----------(7)-----------\
RUN dnf install -y --skip-broken $(dnf provides $(ldd /opt/collectd/lib/collectd/*.so | grep "not found" | awk '{ print "/usr/lib64/"$1 }') | \
            grep --no-group-separator -B 1 "Repo" | grep -v "Repo" | sed 's/-[0-9]\+\..*$//g' | sort | uniq ) && \
        dnf clean all && rm -rf /var/cache/dnf

ENTRYPOINT ["/run_collectd.sh"]
