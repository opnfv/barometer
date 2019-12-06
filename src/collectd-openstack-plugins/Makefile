# makefile to manage COLLECTD_OPENSTACK package
#

# Copyright 2015-2019 Intel Corporation and OPNFV. All rights reserved.
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
#   Martin Klozik, Intel Corporation.

include ../mk/master.mk
include ../package-list.mk

.PHONY: force_make install

WORK_DIR = collectd-openstack-plugins
TAG_DONE_FLAG = $(WORK_DIR)/.$(COLLECTD_OPENSTACK_TAG).tag.done

all: force_make install
	@echo "Finished making $(WORK_DIR) "

INSTALL_TARGET = force_make

force_make: $(WORK_DIR)
	@echo "force make"
	$(AT)cd $(WORK_DIR) && git checkout $(COLLECTD_OPENSTACK_TAG)
	@echo "Make done"

install:
	@echo "install done"

# hard way to clean and clobber
clean:
	$(AT)cd $(WORK_DIR) && git clean -xfd *.o
clobber:
	$(AT)rm -rf $(WORK_DIR)

# distclean is for developer who would like to keep the
# clone git repo, saving time to fetch again from url
distclean:
	$(AT)cd $(WORK_DIR) && git clean -xfd && git checkout -f

test:
	@echo "Make test in $(WORK_DIR) (stub) "

sanity:
	@echo "Make sanity in $(WORK_DIR) (stub) "

$(WORK_DIR):
	$(AT)git clone $(COLLECTD_OPENSTACK_URL) $(WORK_DIR)

