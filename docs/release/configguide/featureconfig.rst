.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

========================
Barometer Configuration
========================
This document provides guidelines on how to install and configure Barometer with Apex.
The deployment script installs and enables a series of collectd plugins on the compute node(s),
which collect and dispatch specific metrics and events from the platform.

.. contents::
   :depth: 3
   :local:

Pre-configuration activities
----------------------------
Deploying the Barometer components in Apex is done through the deploy-opnfv command by selecting
a scenario-file which contains the 'barometer: true' option.  These files are located on the Jump
Host in the /etc/opnfv-apex/ folder.  Two scenarios are pre-defined to include Barometer, and they
are: 'os-nosdn-bar-ha.yaml' and 'os-nosdn-bar-noha.yaml'.

.. code:: bash

    $ cd /etc/opnfv-apex
    $ opnfv-deploy -d os-nosdn-bar-ha.yaml -n network_settings.yaml -i inventory.yaml –- debug

Hardware configuration
----------------------
There's no specific Hardware configuration required.  However, the 'intel_rdt' plugin works
only on platforms with Intel CPUs.

Feature configuration
---------------------
All Barometer plugins are automatically deployed on all compute nodes.  There is no option to
selectively install only a subset of plugins.  Any custom disabling or configuration must be done
directly on the compute node(s) after the deployment is completed.

Upgrading the plugin
--------------------
The Barometer components are built-in in the Apex iso image, and respectively the Apex rpms.  There
is no simple way to update only the Barometer plugins in an existing deployment.
