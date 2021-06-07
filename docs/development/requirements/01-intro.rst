.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket, Intel Corporation and others.

Problem Statement
------------------
Providing carrier grade Service Assurance is critical in the network
transformation to a software defined and virtualized network (NFV).
Medium-/large-scale cloud environments account for between hundreds and
hundreds of thousands of infrastructure systems.  It is vital to monitor
systems for malfunctions that could lead to users application service
disruption and promptly react to these fault events to facilitate improving
overall system performance. As the size of infrastructure and virtual resources
grow, so does the effort of monitoring back-ends. SFQM aims to expose as much
useful information as possible off the platform so that faults and errors in
the NFVI can be detected promptly and reported to the appropriate fault
management entity.

The Anuket platform (NFVI) requires functionality to:

* Create a low latency, high performance packet processing path (fast path)
  through the NFVI that VNFs can take advantage of;
* Measure Telco Traffic and Performance KPIs through that fast path;
* Detect and report violations that can be consumed by VNFs and higher level
  EMS/OSS systems

Examples of local measurable QoS factors for Traffic Monitoring which impact
both Quality of Experience and five 9's availability would be (using Metro Ethernet
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

Barometer updated scope
------------------------
The scope of the project is to provide interfaces to support monitoring of the
NFVI. The project will develop plugins for telemetry frameworks to enable the
collection of platform stats and events and relay gathered information to fault
management applications or the VIM. The scope is limited to
collecting/gathering the events and stats and relaying them to a relevant
endpoint. The project will not enforce or take any actions based on the
gathered information.

.. image: barometer_scope.png

Scope of SFQM
^^^^^^^^^^^^^^
**NOTE:** The SFQM project has been replaced by Barometer.
The output of the project will provide interfaces and functions to support
monitoring of Packet Latency and Network Interfaces while the VNF is in service.

The DPDK interface/API will be updated to support:

* Exposure of NIC MAC/PHY Level Counters
* Interface for Time stamp on RX
* Interface for Time stamp on TX
* Exposure of DPDK events

collectd will be updated to support the exposure of DPDK metrics and events.

Specific testing and integration will be carried out to cover:

* Unit/Integration Test plans: A sample application provided to demonstrate packet
  latency monitoring and interface monitoring

The following list of features and functionality will be developed:

* DPDK APIs and functions for latency and interface monitoring
* A sample application to demonstrate usage
* collectd plugins

The scope of the project involves developing the relavant DPDK APIs, OVS APIs,
sample applications, as well as the utilities in collectd to export all the
relavent information to a telemetry and events consumer.

VNF specific processing, Traffic Monitoring, Performance Monitoring and
Management Agent are out of scope.

The Proposed Interface counters include:

* Packet RX
* Packet TX
* Packet loss
* Interface errors + other stats

The Proposed Packet Latency Monitor include:

* Cycle accurate stamping on ingress
* Supports latency measurements on egress

Support for failover of DPDK enabled cores is also out of scope of the current
proposal. However, this is an important requirement and must-have functionality
for any DPDK enabled framework in the NFVI. To that end, a second phase of this
project will be to implement DPDK Keep Alive functionality that would address
this and would report to a VNF-level Failover and High Availability mechanism
that would then determine what actions, including failover, may be triggered.

Consumption Models
^^^^^^^^^^^^^^^^^^^
In reality many VNFs will have an existing performance or traffic monitoring
utility used to monitor VNF behavior and report statistics, counters, etc.

The consumption of performance and traffic related information/events provided
by this project should be a logical extension of any existing VNF/NFVI monitoring
framework. It should not require a new framework to be developed. We do not see
the Barometer gathered metrics and evetns as major additional effort for
monitoring frameworks to consume; this project would be sympathetic to existing
monitoring frameworks. The intention is that this project represents an
interface for NFVI monitoring to be used by higher level fault management
entities (see below).

Allowing the Barometer metrics and events to be handled within existing
telemetry frameoworks makes it simpler for overall interfacing with higher
level management components in the VIM, MANO and OSS/BSS. The Barometer
proposal would be complementary to the Doctor project, which addresses NFVI Fault
Management support in the VIM, and the VES project, which addresses the
integration of VNF telemetry-related data into automated VNF management
systems. To that end, the project committers and contributors for the Barometer
project wish to collaborate with the Doctor and VES projects to facilitate this.
