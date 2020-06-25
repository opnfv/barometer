# Copyright (c) 2020 Intel Corporation and OPNFV.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

ARG COLLECTD_IMAGE=opnfv/barometer-collectd-experimental

FROM $COLLECTD_IMAGE

ENV tests /src/barometer/docker/barometer-collectd-plugin-tests

WORKDIR /tests/
RUN pip3 install pytest

ENTRYPOINT ["pytest",  "-v"]
