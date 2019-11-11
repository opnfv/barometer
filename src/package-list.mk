# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v16.11

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
# -"master" - development version, based on master branch
# -"experimental" - it is based on master branch as above and includes
#                   set pull requests with experimental features
ifeq ($(COLLECTD_FLAVOR), stable)
# using latest stable release
	COLLECTD_TAG ?= collectd-5.10
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs
else
# 'master' and 'experimental' collectd flavors are both using
# code from master branch
	COLLECTD_TAG ?= master
	SAMPLE_CONF_VARIANT_NAME = collectd_sample_configs-master
ifeq ($(COLLECTD_FLAVOR), experimental)
# 'experimental' flavor is using additional Pull Requests that
# are put on top of master release
	COLLECTD_USE_EXPERIMENTAL_PR ?= y
endif #end of experimental-branch handling
endif

COLLECTD_OPENSTACK_URL ?= https://github.com/openstack/collectd-openstack-plugins
COLLECTD_OPENSTACK_TAG ?= stable/pike
