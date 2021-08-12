.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

===================
Older Release Notes
===================

This document provides the release notes for Euphrates release of Barometer.


Important notes
-----------------
None to date.

Summary
------------
The Barometer@OPNFV project adds a platform telemetry agent to compute nodes
that is capable of retrieving platform statistics and events, and relay them
to Openstack Gnocchi and Aodh. The telemetry agent currently supported by barometer
is collectd. Some additional collectd plugins and application were developed to add
the following functionality:

Write/publishing Plugins:

- aodh plugin: A notification plugin that pushes events to Aodh, and
  creates/updates alarms appropriately.
- SNMP agent plugin: A write plugin that will act as an AgentX subagent that
  receives and handles queries from SNMP master agent and returns the data
  collected by read plugins. The SNMP Agent plugin handles requests only for OIDs
  specified in configuration file. To handle SNMP queries the plugin gets data
  from collectd and translates requested values from collectd’s internal format
  to SNMP format. Supports SNMP: get, getnext and walk requests.
- gnocchi plugin: A write plugin that pushes the retrieved stats to Gnocchi.
  It’s capable of pushing any stats read through collectd to Gnocchi, not just
  the DPDK stats.

Read Plugins:

- Intel RDT plugin: A read plugin that provides the last level cache
  utilization and memory bandwidth utilization.
- virt plugin: A read plugin that uses virtualization API libvirt to gather
  statistics and events about virtualized guests on a system directly from the
  hypervisor, without a need to install collectd instance on the guest.
- Open vSwitch stats plugin: A read plugin that retrieves interface stats from
  OVS.

In addition to the previous plugins from the Danube Release described below.

Release Data
---------------

+--------------------------------------+--------------------------------------+
| **Project**                          | Euphrates/barometer/barometer@opnfv  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | barometer/opnfv-5.1.0                |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Euphrates 5.1.0                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     | December 15th, 2017                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Purpose of the delivery**          | Official OPNFV release               |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Version change
^^^^^^^^^^^^^^^^

Module version changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- There have been no version changes.

Document version changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Reason for version
^^^^^^^^^^^^^^^^^^^^
Feature additions
~~~~~~~~~~~~~~~~~~~~~~~

**JIRA BACK-LOG:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-51                         | RDT Cache Feature                    |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-53                         | RAS Metrics and Events/              |
|                                      | MCELOG Memory Errors                 |
+--------------------------------------+--------------------------------------+
| BAROMETER-55                         | Libvirt Metrics and Events           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-56                         | Openvswitch Mrtics and Events        |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-59                         | AODH plugin                          |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-60                         | Gnocchi Plugin                       |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-58                         | SNMP Agent                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Bugs
~~~~

**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-80                         | SNMP Agent testing with Intel RDT,   |
|                                      | MCELOG, Hugepages, and OVS Stats not |
|                                      | functional in the Apex image of OPNFV|
|                                      | Release E                            |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Deliverables
----------------

Software deliverables
^^^^^^^^^^^^^^^^^^^^^^^

Features to Date
~~~~~~~~~~~~~~~~

Release B
~~~~~~~~~~
The features implemented for OPNFV release B (as part of SFQM) in DPDK include:

* Callback API to enable TX/RX timestamping to measure latency through DPDK.
* Extended NIC statistics API for 1GB, 10GB and 40GB NICs to expose detailed
  statistics for DPDK interfaces in addition to the overall aggregate statistics.
* DPDK Keep Alive.

Release C
~~~~~~~~~~
The features implemented for OPNFV release C (as part of SFQM) include:

* DPDK extended NIC stats API improvement; migrate from key value pairs to
  using id value pairs.
* DPDK Keep Alive improvement, so that core status is exposed through a posix
  shared memory object.
* collectd dpdkstat plugin that can retrieve DPDK interface statistics.
* collectd ceilometer plugin that can publish any statistics collected by
  collectd to ceilometer.
* Fuel plugin support for the collectd ceilometer plugin for OPNFV.

Release D
~~~~~~~~~
The features implemented for OPNFV release D include:

* collectd hugepages plugin that can retrieves the number of available and free hugepages
  on a platform as well as what is available in terms of hugepages per socket.
* collectd Open vSwitch Events plugin that can retrieves events from OVS.
* collectd mcelog plugin that can use mcelog client protocol to check for memory Machine
  Check Exceptions and sends the stats for reported exceptions.
* collectd ceilometer plugin that can publish any statistics collected by
  collectd to ceilometer.

Documentation deliverables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Configuration guide
- User guide
- Release notes
- Scenario documentation.

Known Limitations, Issues and Workarounds
--------------------------------------------

System Limitations
^^^^^^^^^^^^^^^^^^^^

For Intel RDT plugin, compute node needs to support Intel RDT.

Known issues
^^^^^^^^^^^^^^^

No known issues to date.

**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Workarounds
^^^^^^^^^^^^^^^^^

- None to date.

Test Result
---------------

Barometer@OPNFV Euphrates has undergone QA test runs with the following results:

+--------------------------------------+--------------------------------------+
| **TEST-SUITE**                       | **Results:**                         |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| barometercollectd                    |                                      |
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

References
------------
