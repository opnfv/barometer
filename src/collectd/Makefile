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

WORK_DIR = collectd
TAG_DONE_FLAG = $(WORK_DIR)/.$(COLLECTD_TAG).done
BUILD_CMD = ./build.sh
CONFIG_CMD =
CONFIG_CMD += ./configure

LIBPQOS_DIR = $(shell echo $$LIBPQOS_DIR)
ifeq ($(LIBPQOS_DIR),)
LIBPQOS_DIR = /usr
endif

XDG_CACHE_HOME_DIR = $(shell echo $$XDG_CACHE_HOME)
ifeq ($(XDG_CACHE_HOME_DIR),)
XDG_CACHE_HOME_DIR = $(shell echo $$HOME)
endif

ifeq ($(COLLECTD_FLAVOR),collectd-6)
CONFIG_CMD += --enable-cpu
CONFIG_CMD += --enable-interface
CONFIG_CMD += --enable-memory
CONFIG_CMD += --enable-ping
CONFIG_CMD += --enable-uptime

CONFIG_CMD += --disable-aggregation
CONFIG_CMD += --disable-amqp
CONFIG_CMD += --disable-amqp1
CONFIG_CMD += --disable-barometer
CONFIG_CMD += --disable-check_uptime
CONFIG_CMD += --disable-csv
CONFIG_CMD += --disable-curl_xml
CONFIG_CMD += --disable-gmond
CONFIG_CMD += --disable-grpc
CONFIG_CMD += --disable-java
CONFIG_CMD += --disable-lua
CONFIG_CMD += --disable-match_empty_counter
CONFIG_CMD += --disable-match_hashed
CONFIG_CMD += --disable-match_regex
CONFIG_CMD += --disable-match_timediff
CONFIG_CMD += --disable-match_value
CONFIG_CMD += --disable-modbus
CONFIG_CMD += --disable-mqtt
CONFIG_CMD += --disable-network
CONFIG_CMD += --disable-openldap
CONFIG_CMD += --disable-perl
CONFIG_CMD += --disable-postgresql
CONFIG_CMD += --disable-python
CONFIG_CMD += --disable-redis
CONFIG_CMD += --disable-rrdcached
CONFIG_CMD += --disable-rrdtool
CONFIG_CMD += --disable-snmp
CONFIG_CMD += --disable-snmp_agent
CONFIG_CMD += --disable-statsd
CONFIG_CMD += --disable-target_notification
CONFIG_CMD += --disable-target_replace
CONFIG_CMD += --disable-target_scale
CONFIG_CMD += --disable-target_set
CONFIG_CMD += --disable-target_v5upgrade
CONFIG_CMD += --disable-threshold
CONFIG_CMD += --disable-write_graphite
CONFIG_CMD += --disable-write_influxdb_udp
CONFIG_CMD += --disable-write_kafka
CONFIG_CMD += --disable-write_mongodb
CONFIG_CMD += --disable-write_prometheus
CONFIG_CMD += --disable-write_redis
CONFIG_CMD += --disable-write_riemann
CONFIG_CMD += --disable-write_sensu
CONFIG_CMD += --disable-write_syslog
CONFIG_CMD += --disable-write_tsdb
CONFIG_CMD += --enable-debug
else
CONFIG_CMD += --enable-syslog
CONFIG_CMD += --enable-logfile
CONFIG_CMD += --with-libpqos=$(LIBPQOS_DIR)
CONFIG_CMD += --enable-hugepages
CONFIG_CMD += --with-libjevents=/usr/local
CONFIG_CMD += --enable-exec
CONFIG_CMD += --enable-python
CONFIG_CMD += --enable-threshold
CONFIG_CMD += --enable-write_redis
CONFIG_CMD += --disable-perl
CONFIG_CMD += --with-librdkafka=/usr
CONFIG_CMD += --disable-lvm
endif

ifdef WITH_DPDK
CONFIG_CMD += LIBDPDK_CFLAGS='-mssse3'
endif

.PHONY: install force_install config force_make

# install depends on make
force_install: force_make

all: force_make
	@echo "Finished making $(WORK_DIR)"

config $(WORK_DIR)/Makefile: $(WORK_DIR)/configure
	@echo "Configuring with: " $(CONFIG_CMD)
	$(AT)cd $(WORK_DIR); $(CONFIG_CMD)
	@echo "Configure done"

force_make: $(WORK_DIR)/Makefile
	$(AT) $(MAKE) -C $(WORK_DIR) $(MORE_MAKE_FLAGS)
	@echo "Make done"

force_install:
	$(AT)$(MAKE) -C $(WORK_DIR) install
ifndef DOCKER
	$(AT)cp $(WORK_DIR)/contrib/systemd.collectd.service /etc/systemd/system/
	$(AT)mv /etc/systemd/system/systemd.collectd.service /etc/systemd/system/collectd.service
	$(AT)sed -i -e 's/ExecStart=\/usr\/sbin\/collectd/ExecStart=\/opt\/collectd\/sbin\/collectd/g' /etc/systemd/system/collectd.service
	$(AT)sed -i -e 's/CapabilityBoundingSet=/CapabilityBoundingSet=CAP_SETUID CAP_SETGID CAP_SYS_RAWIO CAP_SYS_ADMIN/g' /etc/systemd/system/collectd.service
	$(AT)sed -i -e 's|Environment=\(.*\)|Environment=XDG_CACHE_HOME='$(XDG_CACHE_HOME_DIR)' \1|g' /etc/systemd/system/collectd.service
	$(AT)systemctl daemon-reload
endif
	$(AT)sudo ./ovs_pmd_stats_config.sh
	$(AT)sudo ./snmp_mib_config.sh

	@echo "Using sample configs: $(SAMPLE_CONF_VARIANT_NAME)"
	$(AT)sudo ./include_config.sh $(SAMPLE_CONF_VARIANT_NAME)
	@echo "Make install done"

install: force_install


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

.PHONY: boot
# boot collectd is the process to produce the script 'configure'
boot $(WORK_DIR)/configure: $(TAG_DONE_FLAG)
	@echo "booting up collectd"
	$(AT)cd $(WORK_DIR); $(BUILD_CMD)
	@echo "done booting collectd"

$(WORK_DIR):
	$(AT)git clone $(COLLECTD_URL)

$(TAG_DONE_FLAG): $(WORK_DIR)
	@echo "Checking out collectd from tag: $(COLLECTD_TAG)"
	$(AT)cd collectd; git checkout $(COLLECTD_TAG)
ifneq ($(PATCH_FILE),)
	$(AT)cd $(WORK_DIR); patch -p1 < ../$(PATCH_FILE)
endif
ifeq ($(COLLECTD_USE_EXPERIMENTAL_PR), y)
	@echo "Applying experimental pull requests"
	$(AT)cd $(WORK_DIR); ../collectd_apply_pull_request.sh
endif
	$(AT)touch $@
