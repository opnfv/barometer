.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV os-nosdn-bar-noha
===================================

This document provides details of the scenario for Euphrates of Barometer.

.. contents::
   :depth: 3
   :local:

Introduction
---------------
.. In this section explain the purpose of the scenario and the types of
.. capabilities provided

This scenario has the features from the Barometer project. Collectd (a telemetry agent) isinstalled on compute nodes so that its statistics, events and alarming services can be relayed to Gnoochi and Aodh. These are the first steps in paving the way for Platform (NFVI) Monitoring in OPNFV.

Scenario components and composition
-------------------------------------
.. In this section describe the unique components that make up the scenario,
.. what each component provides and why it has been included in order
.. to communicate to the user the capabilities available in this scenario.

This scenario deploys the High Availability OPNFV Cloud based on the
configurations provided in `os-nosdn-bar-noha.yaml`.
This yaml file contains configurations and is passed as an
argument to `overcloud-deploy-function.sh` script.
This scenario deploys multiple nodes: 1 Controller, 2 Computes.

Collectd is installed on compute nodes and Openstack services runs on controller node.

Barometer can be added to the scenario by adding/updating `barometer: true` line under `deploy options` in `os-nosdn-fdio-noha.yaml` file. 

os-nosdn-bar-noha scenario is successful when all the nodes are accessible, up and running. Also, verify if plugins/services are communicating with Gnocchi and Aodh on controller nodes. 

Scenario usage overview
----------------------------
.. Provide a brief overview on how to use the scenario and the features available to the
.. user.  This should be an "introduction" to the userguide document, and explicitly link to it,
.. where the specifics of the features are covered including examples and API's

After installation, plugins will be able to read/write the stats on/from controller node. A detailed list of supported plugins along with their sample configuration can be found in userguide. 

Limitations, Issues and Workarounds
---------------------------------------
.. Explain scenario limitations here, this should be at a design level rather than discussing
.. faults or bugs.  If the system design only provide some expected functionality then provide
.. some insight at this point.

References
-----------------


