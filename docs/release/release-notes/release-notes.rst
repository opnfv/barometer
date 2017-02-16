.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================================================================
OPNFV Barometer Release Notes
======================================================================

This document provides the release notes for Danube Release of Barometer.

.. contents::
   :depth: 3
   :local:


Version history
------------------

+--------------------+--------------------+--------------------+--------------------+
| **Date**           | **Ver.**           | **Author**         | **Comment**        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+
| 2017-02-16         | 0.1.0              | Maryam Tahhan      | First draft        |
|                    |                    |                    |                    |
+--------------------+--------------------+--------------------+--------------------+

Important notes
-----------------
None to date.

Summary
------------
The Barometer@OPNFV project adds a platform telemetry agent to compute nodes
that is capabable of retrieving platform statistics and events, and relay them
to Openstack ceilometer. The telemetry agent currently supported by Barometer
is collectd. Some additional collectd plugin were developed to add functionality
to retrieve statistics or events for:

- Hugepages
- mcelog memory machine check exceptions
- Open vSwitch events
- Ceilometer

Release Data
---------------

+--------------------------------------+--------------------------------------+
| **Project**                          | Danube/barometer/barometer@opnfv     |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Repo/commit-ID**                   | barometer/                           |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| **Release designation**              | Danube 1.0                           |
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
| BAROMETER-38                         | RAS Collectd Plugin                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-41                         | OVS Collectd Plugin                  |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-43                         | Fuel Plugin for D Release            |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
| BAROMETER-48                         | Hugepages Plugin for Collectd        |
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

This section provides a summary of the features implemented to date and their
relevant upstream projects.

.. Figure:: Features_to_date1.png

   Barometer features to date

.. Figure:: Features_to_date2.png

   Barometer features to date cont.

Please note the timeline denotes DPDK releases.

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

Barometer has the same limiations as the fuel project in general as regards

- **Max number of blades*

- **Min number of blades**

- **Storage**

- **Max number of networks**

- **L3Agent**

The only additional limitiation is the following:

**Telemetry:** Ceilometer service needs to be configured for compute nodes.

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

Barometer@OPNFV Danube RC1 has undergone QA test runs with the following results:

+--------------------------------------+--------------------------------------+
| **TEST-SUITE**                       | **Results:**                         |
|                                      |                                      |
+--------------------------------------+--------------------------------------+
|                                      |                                      |
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

For more information on the OPNFV Danube release, please see:

http://opnfv.org/danube

