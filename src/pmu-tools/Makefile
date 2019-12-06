# makefile to manage collectd package
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

include ../mk/master.mk
include ../package-list.mk
export XDG_CACHE_HOME=/usr/local/src
WORK_DIR = pmu-tools
TAG_DONE_FLAG = $(WORK_DIR)/.$(PMUTOOLS_TAG).done
BUILD_CMD =
MAKEFILE = Makefile

.PHONY: install force_install force_make

# install depends on make
force_install: force_make

all: force_make
	@echo "Finished making $(WORK_DIR) "

INSTALL_TARGET = force_install force_make

force_make: $(WORK_DIR) $(TAG_DONE_FLAG)
	$(AT)cd $(WORK_DIR) && git pull $(PMUTOOLS_URL) $(PMUTOOLS_TAG)
	@echo "git pull done"
	$(AT)cd $(WORK_DIR)/jevents
	$(AT)sed -i 's/lib64/lib/' $(WORK_DIR)/jevents/$(MAKEFILE)
	$(AT)sed -i 's/CFLAGS := -g -Wall -O2 -Wno-unused-result/CFLAGS := -g -Wall -O2 -Wno-unused-result -fPIC/' $(WORK_DIR)/jevents/$(MAKEFILE)
	$(AT)$(MAKE) -C $(WORK_DIR)/jevents
	@echo "Make done"

force_install:
	$(AT)sudo $(MAKE) -C $(WORK_DIR)/jevents install
	$(AT)./$(WORK_DIR)/event_download.py --all

install: $(INSTALL_TARGET)

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
	$(AT)git clone $(PMUTOOLS_URL)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(PMUTOOLS_TAG)
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
	$(AT)touch $@
