# makefile to manage dpdk package
#

# Copyright 2015-2016 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Contributors:
#   Aihua Li, Huawei Technologies.
#   Martin Klozik, Intel Corporation.

include ../mk/master.mk
include ../package-list.mk

.PHONY: install force_make

WORK_DIR = dpdk
TAG_DONE_FLAG = $(WORK_DIR)/.$(DPDK_TAG).tag.done

DPDK_TARGET = x86_64-native-linuxapp-gcc
CONFIG_FILE_LINUXAPP = $(WORK_DIR)/config/common_base

all: force_make install
	@echo "Finished making $(WORK_DIR) "

INSTALL_TARGET = force_make

# modify CONFIG_FILE to enable SHARED_LIB build and restore original CONFIG_FILE after the build
# DPDK v16 comments:
## CONFIG_RTE_BUILD_COMBINE_LIBS has been obsoleted
## CONFIG_RTE_LIBRTE_VHOST and CONFIG_RTE_LIBRTE_KNI are listed in both config_base and config_linuxapp,
## values from config_linuxapp will be used, but options are modified at both places to avoid confusion.
force_make: $(TAG_DONE_FLAG)
	$(AT)cd $(WORK_DIR) && git pull $(DPDK_URL) $(DPDK_TAG)
	$(AT)sed -i -e 's/CONFIG_RTE_BUILD_SHARED_LIB=./CONFIG_RTE_BUILD_SHARED_LIB=y/g' $(CONFIG_FILE_LINUXAPP)
	$(AT)sed -i -e 's/CONFIG_RTE_EAL_PMD_PATH=.*/CONFIG_RTE_EAL_PMD_PATH=\"\/usr\/lib\/dpdk-pmd\/\"/g' $(CONFIG_FILE_LINUXAPP)
	$(AT)sed -i -e 's/CONFIG_RTE_LIBRTE_KNI=./CONFIG_RTE_LIBRTE_KNI=n/g' $(CONFIG_FILE_LINUXAPP)
	$(AT)cd $(WORK_DIR); make config T=$(DPDK_TARGET) -j; make -j
	$(AT)cd `dirname $(CONFIG_FILE_LINUXAPP)` && git checkout `basename $(CONFIG_FILE_LINUXAPP)` && cd -
	@echo "Make done"

install: $(INSTALL_TARGET)
	$(AT)cd $(WORK_DIR); sudo make -j install prefix=/usr; cd -
	$(AT)mkdir -p /usr/lib/dpdk-pmd
	$(AT)find /usr/lib -type f -name 'librte_pmd*' | while read path; do ln -fs $$path /usr/lib/dpdk-pmd/$$(echo $$path | grep -o 'librte_.*so'); done
	$(AT)echo 0 > /proc/sys/kernel/randomize_va_space
	$(AT)sudo cp -a $(WORK_DIR)/build/kmod $(INSTALL_DIR)/lib/modules/$(KERNEL_VERSION)
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
	$(AT)git clone $(DPDK_URL)

$(TAG_DONE_FLAG): $(WORK_DIR)
	$(AT)cd $(WORK_DIR); git checkout $(DPDK_TAG)
	$(AT)touch $@
