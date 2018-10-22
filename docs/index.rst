.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

=========
Barometer
=========

:Project: `Barometer`_

:Authors: Maryam Tahhan <maryam.tahhan@intel.com>

:History:

          ========== =====================================================
           Date       Description
          ========== =====================================================
          16.12.2014 Project creation
          ========== =====================================================

Barometer is the project that renames Software Fastpath service Quality Metrics
(SFQM) and updates its scope which was networking centric.

The goal of SFQM was to develop the utilities and libraries in DPDK to
support:

* Measuring Telco Traffic and Performance KPIs. Including:

  * Packet Delay Variation (by enabling TX and RX time stamping).
  * Packet loss (by exposing extended NIC stats).

* Performance Monitoring of the DPDK interfaces (by exposing
  extended NIC stats + collectd Plugin).
* Detecting and reporting violations that can be consumed by VNFs
  and higher level management systems (through DPDK Keep Alive).

With Barometer the scope is extended to monitoring the NFVI. The ability to
monitor the Network Function Virtualization Infrastructure (NFVI) where VNFs
are in operation will be a key part of Service Assurance within an NFV
environment, in order to enforce SLAs or to detect violations, faults or
degradation in the performance of NFVI resources so that events and relevant
metrics are reported to higher level fault management systems.
If physical appliances are going to be replaced by virtualized appliances
the service levels, manageability and service assurance needs to remain
consistent or improve on what is available today. As such, the NFVI needs to
support the ability to monitor:

* Traffic monitoring and performance monitoring of the components that provide
  networking functionality to the VNF, including: physical interfaces, virtual
  switch interfaces and flows, as well as the virtual interfaces themselves and
  their status, etc.
* Platform monitoring including: CPU, memory, load, cache, themals, fan speeds,
  voltages and machine check exceptions, etc.

All of the statistics and events gathered must be collected in-service and must
be capable of being reported by standard Telco mechanisms (e.g. SNMP), for
potential enforcement or correction actions. In addition, this information
could be fed to analytics systems to enable failure prediction, and can also be
used for intelligent workload placement.

All developed features will be upstreamed to Open Source projects relevant to
telemetry such as `collectd`_, and relevant Openstack projects.

.. toctree::
     :maxdepth: 3

     ./release/configguide/index.rst
     ./release/scenarios/index.rst
     ./release/userguide/index.rst
     ./release/release-notes/index.rst
     ./development/requirements/index.rst
     ./development/design/index.rst
     ./development/testing/index.rst

Indices
=======
* :ref:`search`

.. _Barometer: https://wiki.opnfv.org/display/fastpath
.. _collectd: http://collectd.org/
