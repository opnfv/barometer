# Copyright (c) 2020 Intel Corporation and OPNFV.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

FROM opnfv/barometer-collectd-tests-base:latest

ENV COLLECTD_FLAVOR tests
ENV WITH_DPDK y
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins
ENV tests /src/barometer/docker/barometer-collectd-plugin-tests

WORKDIR ${openstack_plugins}
RUN make && \
        pip3 install --upgrade pip && \
        pip3 install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt


COPY docker/barometer-collectd-plugin-tests/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh


COPY docker/barometer-collectd-plugin-tests/commands.sh /scripts/commands.sh
RUN ["chmod", "+x", "/scripts/commands.sh"]
ENTRYPOINT ["/scripts/commands.sh"]
