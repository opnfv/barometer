Introduction
============

The goal of Software Fastpath service Quality Metrics (SFQM) is to
develop the utilities and libraries in `DPDK`_ to support:

* Measuring Telco Traffic and Performance KPIs. Including:

  * Packet Delay Variation (by enabling TX and RX time stamping).
  * Packet loss (by exposing extended NIC stats).

* Performance Monitoring of the DPDK interfaces (by exposing
  extended NIC stats + collectd Plugin).
* Detecting and reporting violations that can be consumed by VNFs
  and higher level management systems (through DPDK Keep Alive).

After all **the ability to measure and enforce Telco KPIs (Service
assurance) in the data-plane will be mandatory for any Telco grade NFVI
implementation**.

All developed features will be upstreamed to `DPDK`_ or other Open
Source projects relevant to telemetry such as `collectd`_ and fault
management such as `Monasca`_ and/or `Ceilometer`_.

The OPNFV project wiki can be found @ `SFQM`_

Problem Statement
==================
The OPNFV platform (NFVI) requires functionality to:

* Create a low latency, high performance packet processing path (fast path)
  through the NFVI that VNFs can take advantage of;
* Measure Telco Traffic and Performance KPIs through that fast path;
* Detect and report violations that can be consumed by VNFs and higher level
  EMS/OSS systems

Examples of local measurable QoS factors for Traffic Monitoring which impact
both Quality of Experience and 5’9s availability would be (using Metro Ethernet
Forum Guidelines as reference):

* Packet loss
* Packet Delay Variation
* Uni-directional frame delay

Other KPIs such as Call drops, Call Setup Success Rate, Call Setup time etc. are
measured by the VNF.

In addition to Traffic Monitoring, the NFVI must also support Performance
Monitoring of the physical interfaces themselves (e.g. NICs), i.e. an ability to
monitor and trace errors on the physical interfaces and report them.

All these traffic statistics for Traffic and Performance Monitoring must be
measured in-service and must be capable of being reported by standard Telco
mechanisms (e.g. SNMP traps), for potential enforcement actions.

Scope
======
The output of the project will provide interfaces and functions to support
monitoring of Packet Latency and Network Interfaces while the VNF is in service.

The DPDK interface/API will be updated to support:

* Exposure of NIC MAC/PHY Level Counters
* Interface for Time stamp on RX
* Interface for Time stamp on TX

Specific testing and integration will be carried out to cover:

* Unit/Integration Test plans: A sample application provided to demonstrate packet
  latency monitoring and interface monitoring

The following list of features and functionality will be developed:

* DPDK APIs and functions for latency and interface monitoring
* A sample application to demonstrate usage

The scope of the project is limited to the DPDK APIs and a sample application to
demonstrate usage.

.. Figure:: telcokpis_update.png

   Architecture overview (showing provided functionality in green)

In the figure above, the interfaces 1, 2, 3 are implemented along with a sample
application. The sample application will support monitoring of NIC
counters/status and will also support measurement of packet latency using DPDK
provided interfaces.

VNF specific processing, Traffic Monitoring, Performance Monitoring and
Management Agent are out of scope. The scope is limited to Intel 10G Niantic
support.

The Proposed MAC/PHY Interface Counters include:

* Packet RX
* Packet TX
* Packet loss
* Interface errors + other stats

The Proposed Packet Latency Monitor include:

* Cycle accurate ‘stamping’ on ingress
* Supports latency measurements on egress

Support for additional types of Network Interfaces can be added in the future.

Support for failover of DPDK enabled cores is also out of scope of the current
proposal. However, this is an important requirement and must-have functionality
for any DPDK enabled framework in the NFVI. To that end, a second phase of this
project will be to implement DPDK “Keep Alive” functionality that would address
this and would report to a VNF-level Failover and High Availability mechanism
that would then determine what actions, including failover, may be triggered.

Consumption Models
===================
Fig 1.1 shows how a sample application will be provided to demonstrate
usage. In reality many VNFs will have an existing performance or traffic
monitoring utility used to monitor VNF behavior and report statistics, counters,
etc.

To consume the performance and traffic related information provided within the
scope of this project should in most cases be a logical extension of any
existing VNF performance or traffic monitoring utility, in most cases it should
not require a new utility to be developed. We do not see the Software Fastpath
Service Quality Metrics data as major additional effort for VNFs to consume,
this project would be sympathetic to existing VNF architecture constructs. The
intention is that this project represents a lower level interface for network
interface monitoring to be used by higher level fault management entities (see
below).

Allowing the Software Fastpath Service Quality Metrics data to be handled within
existing VNF performance or traffic monitoring utilities also makes it simpler
for overall interfacing with higher level management components in the VIM, MANO
and OSS/BSS. The Software Fastpath Service Quality Metrics proposal would be
complementary to the Fault Management and Maintenance project proposal
(“Doctor”) which is also in flight, which addresses NFVI Fault Management
support in the VIM. To that end, the project committers and contributors for the
Software Fastpath Service Quality Metrics project wish to work in sync with the
“Doctor” project – to facilitate this, one of the “Doctor” contributors has also
been added as a contributor to the Software Fastpath Service Quality Metrics
project.

.. _SFQM: https://wiki.opnfv.org/collaborative_development_projects/opnfv_telco_kpi_monitoring
.. _DPDK: http://dpdk.org/
.. _collectd: http://collectd.org/
.. _Monasca: https://wiki.openstack.org/wiki/Monasca
.. _Ceilometer: https://wiki.openstack.org/wiki/Telemetry
