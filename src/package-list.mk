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

# collectd section
COLLECTD_URL ?= https://github.com/collectd/collectd
COLLECTD_TAG ?= master

COLLECTD_OPENSTACK_URL ?= https://github.com/openstack/collectd-openstack-plugins
COLLECTD_OPENSTACK_TAG ?= stable/pike
