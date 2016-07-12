# Upstream Package List
#
# Everything here is defined as its suggested default
# value, it can always be overriden when invoking Make

# dpdk section
# DPDK_URL ?= git://dpdk.org/dpdk
DPDK_URL ?= http://dpdk.org/git/dpdk
DPDK_TAG ?= v16.04

# collectd section
COLLECTD_URL ?= https://github.com/maryamtahhan/collectd-with-DPDK
COLLECTD_TAG ?= dpdkstat

COLLECTD_CEILOMETER_URL ?= https://github.com/openstack/collectd-ceilometer-plugin
COLLECTD_CEILOMETER_TAG ?= master
