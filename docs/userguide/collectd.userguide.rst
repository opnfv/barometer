.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

collectd plugins
=================
Barometer has enabled the following collectd plugins:

* dpdkstat plugin: A read plugin that retrieve stats from the DPDK extended
   NIC stats API.

* `ceilometer plugin`_: A write plugin that pushes the retrieved stats to
  Ceilometer. It's capable of pushing any stats read through collectd to
  Ceilometer, not just the DPDK stats.

* hugepages plugin:  A read plugin that retrieves the number of available
  and free hugepages on a platform as well as what is available in terms of
  hugepages per socket.

* RDT plugin: A read plugin that provides the last level cache utilitzation and
  memory bandwidth utilization

* Open vSwitch events Plugin: A read plugin that retrieves events from OVS.

All the plugins above are available on the collectd master, except for the
ceilometer plugin as it's a python based plugin and only C plugins are accepted
by the collectd community. The ceilometer plugin lives in the OpenStack
repositories.

Other plugins under development or existing as a pull request into collectd master:

* dpdkevents:  A read plugin that retrieves DPDK link status and DPDK
  forwarding cores liveliness status (DPDK Keep Alive).

* Open vSwitch stats Plugin: A read plugin that retrieve flow and interface
  stats from OVS.

* mcelog plugin: A read plugin that uses mcelog client protocol to check for
  memory Machine Check Exceptions and sends the stats for reported exceptions.

* SNMP write: A write plugin that will act as a SNMP subagent and will map
  collectd metrics to relavent OIDs. Will only support SNMP: get, getnext and
  walk.

* Legacy/IPMI: A read plugin that will report platform thermals, voltages,
  fanspeed....

Building collectd with the Barometer plugins and installing the dependencies
=============================================================================
The plugins that have been merged to master can all be built and configured through
the barometer repository.

**Note**: sudo permissions are required to install collectd.

**Note**: These are instructions for Ubuntu 16.04.

To build and install these dependencies, clone the barometer repo:

.. code:: c

    $ git clone https://gerrit.opnfv.org/gerrit/barometer

Install the build dependencies

.. code:: bash

    $ ./src/install_build_deps.sh

To install collectd as a service and install all it's dependencies:

.. code:: bash

    $ cd barometer/src && sudo make && sudo make install

This will install collectd as a service and the base install directory
is /opt/collectd.

Sample configuration files can be found in '/opt/collectd/etc/collectd.conf.d'

Please note if you are using any Open vSwitch plugins you need to run:

.. code:: bash

    $ sudo ovs-vsctl set-manager ptcp:6640

Monitoring Interfaces and Openstack Support
-------------------------------------------
.. Figure:: monitoring_interfaces.png

   Monitoring Interfaces and Openstack Support

The figure above shows the DPDK L2 forwarding application running on a compute
node, sending and receiving traffic. collectd is also running on this compute
node retrieving the stats periodically from DPDK through the dpdkstat plugin
and publishing the retrieved stats to Ceilometer through the ceilometer plugin.

To see this demo in action please checkout: `Barometer OPNFV Summit demo`_

References
----------
[1] https://collectd.org/wiki/index.php/Naming_schema
[2] https://github.com/collectd/collectd/blob/master/src/daemon/plugin.h
[3] https://collectd.org/wiki/index.php/Value_list_t
[4] https://collectd.org/wiki/index.php/Data_set
[5] https://collectd.org/documentation/manpages/types.db.5.shtml
[6] https://collectd.org/wiki/index.php/Data_source
[7] https://collectd.org/wiki/index.php/Meta_Data_Interface

.. _Barometer OPNFV Summit demo: https://prezi.com/kjv6o8ixs6se/software-fastpath-service-quality-metrics-demo/
.. _ceilometer plugin: https://github.com/openstack/collectd-ceilometer-plugin/tree/stable/mitaka
