# Top Makefile to build upstream packages.
#

# Copyright 2016-2019 Intel Corporation and OPNFV. All rights reserved.
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

#
# Contributors:
#   Aihua Li, Huawei Technologies.
#   Maryam Tahhan, Intel Corporation.

all clean distclean: subbuilds

subbuilds: $(SUBBUILDS)
$(SUBBUILDS):
	$(AT)mkdir -p ../$@/mk
	$(AT)cp -rf mk/* ../$@/mk
	$(AT)cp -rf package-list.mk ../$@/
	$(AT)cp Makefile.$@ ../$@/Makefile
	$(AT)$(MAKE) -C ../$@ $(MAKECMDGOALS)

with-dpdk:
export WITH_DPDK

include mk/master.mk
# TODO(elfoley) Later on, we can re-enable build from source as a user configured option
SUBDIRS =
#ifdef WITH_DPDK
#SUBDIRS += dpdk
#endif
#SUBDIRS += libpqos
#SUBDIRS += pmu-tools
#SUBDIRS += librdkafka
SUBDIRS += collectd

include mk/make-subsys.mk
