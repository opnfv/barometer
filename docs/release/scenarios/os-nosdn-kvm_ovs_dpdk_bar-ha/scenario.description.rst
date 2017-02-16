.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV os-nosdn-kvm_ovs_dpdk_bar-ha
===================================

This document provides scenario level details for Danube of Barometer.

.. contents::
   :depth: 3
   :local:

Introduction
---------------
.. In this section explain the purpose of the scenario and the types of
.. capabilities provided
This scenario combines the features from the following three projects in a
single instantiation of OPNFV:

- KVM4NFV
- OVS4NFV
- Barometer

A distinguishing factor for this scenario vs other scenarios that integrate
Open vSwitch and KVM is that collectd (a telemetry agent) is installed on
compute nodes so that their statistics and events can be relayed to ceilometer.
These are the first steps in paving the way for Platform (NFVI) Monitoring in
OPNFV.

For Fuel this scenario installs the latest DPDK-enabled Open vSwitch component,
KVM4NFV latest software packages for Linux Kernel and QEMU patches for
achieving low latency, and the collectd telemetry agent.

Scenario components and composition
-------------------------------------
.. In this section describe the unique components that make up the scenario,
.. what each component provides and why it has been included in order
.. to communicate to the user the capabilities available in this scenario.

This scenario deploys the High Availability OPNFV Cloud based on the
configurations provided in ha_nfv-kvm_ovs_bar_heat_ceilometer_scenario.yaml.
This yaml file contains following configurations and is passed as an
argument to deploy.py script

* scenario.yaml:This configuration file defines translation between a
  short deployment scenario name(os-nosdn-kvm_ovs_dpdk_bar-ha) and an actual
  deployment scenario configuration file
  (ha_nfv-kvm_nfv-ovs-dpdk_bar_heat_ceilometer_scenario.yaml)

* deployment-scenario-metadata:Contains the configuration metadata like
  title,version,created,comment.

* stack-extensions:Stack extentions are opnfv added value features in form
  of a fuel-plugin.Plugins listed in stack extensions are enabled and
  configured.

* dea-override-config: Used to configure the HA mode,network segmentation
  types and role to node assignments.These configurations overrides
  corresponding keys in the dea_base.yaml and dea_pod_override.yaml.
  These keys are used to deploy multiple nodes(3 controllers,2 computes)
  as mention below.

* **Node 1**: This node has MongoDB and Controller roles. The controller
  node runs the Identity service, Image Service, management portions of
  Compute and Networking, Networking plug-in and the dashboard. The
  Telemetry service which was designed to support billing systems for
  OpenStack cloud resources uses a NoSQL database to store information.
  The database typically runs on the controller node.

* **Node 2**: This node has Controller and Ceph-osd roles. Ceph is a
  massively scalable, open source, distributed storage system. It is
  comprised of an object store, block store and a POSIX-compliant distributed
  file system. Enabling Ceph,  configures Nova to store ephemeral volumes in
  RBD, configures Glance to use the Ceph RBD backend to store images,
  configures Cinder to store volumes in Ceph RBD images and configures the
  default number of object replicas in Ceph.

* **Node 3**: This node has Controller role in order to achieve high
  availability.

* **Node 4**: This node has Compute role. The compute node runs the
  hypervisor portion of Compute that operates tenant virtual machines
  instances. By default, Compute uses KVM as the hypervisor. Collectd
  will be installed on this node.

* **Node 5**: This node has compute role.

* dha-override-config:Provides information about the VM definition and
  Network config for virtual deployment.These configurations overrides
  the pod dha definition and points to the controller,compute and
  fuel definition files.

* os-nosdn-kvm_ovs_dpdk_bar-ha scenario is successful when all the 5 Nodes are
  accessible, up and running.

Scenario usage overview
----------------------------
.. Provide a brief overview on how to use the scenario and the features available to the
.. user.  This should be an "introduction" to the userguide document, and explicitly link to it,
.. where the specifics of the features are covered including examples and API's

After installation use of the scenario traffic on the private network will
automatically be processed by the upgraded DPDK datapath.

Limitations, Issues and Workarounds
---------------------------------------
.. Explain scenario limitations here, this should be at a design level rather than discussing
.. faults or bugs.  If the system design only provide some expected functionality then provide
.. some insight at this point.

References
-----------------

For more information on the OPNFV Danube release, please visit
http://www.opnfv.org/danube

