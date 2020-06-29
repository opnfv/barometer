# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v18.11

LIBPQOS_URL ?= https://github.com/01org/intel-cmt-cat.git
LIBPQOS_TAG ?= master

PMUTOOLS_URL ?= https://github.com/andikleen/pmu-tools
PMUTOOLS_TAG ?= master

KAFKA_URL ?= https://github.com/edenhill/librdkafka.git
KAFKA_TAG ?= v0.9.5

# collectd section
COLLECTD_URL ?= https://github.com/collectd/collectd

# there are 3 collectd flavors:
# -"stable" - based on stable collectd release
# -"master" - development version, based on main branch
# -"experimental" - it is based on main branch as above and includes
#                   set pull requests with experimental features
ifeq ($(COLLECTD_FLAVOR), stable)
# using latest stable release
	COLLECTD_TAG ?= collectd-5.11
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs
else
# 'latest' and 'experimental' collectd flavors are both using
# code from main branch
	COLLECTD_TAG ?= main
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs-master
ifeq ($(COLLECTD_FLAVOR), experimental)
# 'experimental' flavor is using additional Pull Requests that
# are put on top of main release
	COLLECTD_USE_EXPERIMENTAL_PR ?= y
endif #end of experimental-branch handling
endif

COLLECTD_OPENSTACK_URL ?= https://github.com/openstack/collectd-openstack-plugins
COLLECTD_OPENSTACK_TAG ?= stable/pike
