# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v19.11

LIBPQOS_URL ?= https://github.com/01org/intel-cmt-cat.git
LIBPQOS_TAG ?= master

PMUTOOLS_URL ?= https://github.com/andikleen/pmu-tools
PMUTOOLS_TAG ?= master

KAFKA_URL ?= https://github.com/edenhill/librdkafka.git
KAFKA_TAG ?= v1.5.2

# collectd section
COLLECTD_URL ?= https://github.com/collectd/collectd

# there are 4 collectd flavors:
# -"stable" - based on stable collectd release
# -"latest" - development version, based on main branch
# -"experimental" - it is based on main branch as above and includes
#                   set pull requests with experimental features
# -"collectd-6" - based on the collectd 6.0 branch
ifeq ($(COLLECTD_FLAVOR), stable)
# using the most recent stable release
	COLLECTD_TAG ?= collectd-5.12
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs
endif
ifeq ($(COLLECTD_FLAVOR), latest)
# collectd code from main branch
	COLLECTD_TAG ?= main
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs-latest
endif
ifeq ($(COLLECTD_FLAVOR), experimental)
# 'experimental' flavor is using additional Pull Requests that
# are put on top of main release
	COLLECTD_TAG ?= main
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs-latest
	COLLECTD_USE_EXPERIMENTAL_PR ?= y
endif #end of experimental-branch handling
ifeq ($(COLLECTD_FLAVOR), collectd-6)
# 'collectd-6' flavor is using collectd-6.0 branch
	COLLECTD_TAG ?= collectd-6.0
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs-latest
	COLLECTD_USE_EXPERIMENTAL_PR ?= y
endif #end of collectd-6.0-branch handling

@echo "Using COLLECTD_TAG: $(COLLECTD_TAG)"
@echo "Using SAMPLE_CONF_VARIANT_NAME: $(SAMPLE_CONF_VARIANT_NAME)"
