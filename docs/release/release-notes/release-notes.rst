.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================================================================
OPNFV Barometer Release Notes
======================================================================

This document provides the release notes for Euphrates Release of Barometer.

.. contents::
   :depth: 3
   :local:


Version history
------------------

+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-08-25         | 0.1.0              | Shobhi Jain        | First draft        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+

Important notes
-----------------
None to date.

Summary
------------
The Barometer@OPNFV project adds a platform telemetry agent to compute nodes
that is capabable of retrieving platform statistics and events, and relay them
to Openstack Gnocchi and Aodh. The telemetry agent currently supported by barometer
is Collectd. Some additional collectd plugins and application were developed to add
functionality to retrieve statistics or events for:

Write Plugins: aodh plugin, SNMP agent plugin, gnocchi plugin.

Read Plugins/application: Intel RDT plugin, virt plugin, Open vSwitch stats plugin,
Open vSwitch PMD stats application.

Release Data
---------------

+--------------------------------------+--------------------------------------+
| **Project**                          | Euphrates/barometer/barometer@opnfv  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | barometer/                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Euphrates 1.0                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release date**                     |                                      |
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
- The Barometer@OPNFV installation guide version has changed from version 0.1 to to 0.2

Reason for version
^^^^^^^^^^^^^^^^^^^^
Feature additions
~~~~~~~~~~~~~~~~~~~~~~~

**JIRA BACK-LOG:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-78                         | Barometer + Doctor Collaboration     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
+--------------------------------------+--------------------------------------+

Bug corrections
~~~~~~~~~~~~~~~~~~~~~

**JIRA TICKETS:**

+--------------------------------------+--------------------------------------+
| **JIRA REFERENCE**                   | **SLOGAN**                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
|                                      |                                      |
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
The features implemented for OPNFV release D (as part of SFQM) include:

* collectd hugepages plugin that can retrieves the number of available and free hugepages   on a platform as well as what is available in terms of hugepages per socket.
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
