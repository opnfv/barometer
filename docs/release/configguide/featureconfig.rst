.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=============================
Barometer Configuration Guide
=============================
This document provides guidelines on how to install and configure Barometer with Apex and Compass4nfv.
The deployment script installs and enables a series of collectd plugins on the compute node(s),
which collect and dispatch specific metrics and events from the platform.

Pre-configuration activities - Apex
-----------------------------------
Deploying the Barometer components in Apex is done through the deploy-opnfv command by selecting
a scenario-file which contains the ``barometer: true`` option.  These files are located on the
Jump Host in the ``/etc/opnfv-apex/ folder``.  Two scenarios are pre-defined to include Barometer,
and they are: ``os-nosdn-bar-ha.yaml`` and ``os-nosdn-bar-noha.yaml``.

.. code:: bash

    $ cd /etc/opnfv-apex
    $ opnfv-deploy -d os-nosdn-bar-ha.yaml -n network_settings.yaml -i inventory.yaml –- debug

Pre-configuration activities - Compass4nfv
------------------------------------------
Deploying the Barometer components in Compass4nfv is done by running the deploy.sh script after
exporting a scenario-file which contains the ``barometer: true`` option. Two scenarios are pre-defined
to include Barometer, and they are: ``os-nosdn-bar-ha.yaml`` and ``os-nosdn-bar-noha.yaml``. For more
information, please refer to these useful links:
https://github.com/opnfv/compass4nfv
https://wiki.opnfv.org/display/compass4nfv/Compass+101
https://wiki.opnfv.org/display/compass4nfv/Containerized+Compass

The quickest way to deploy using Compass4nfv is given below.

.. code:: bash

    $ export SCENARIO=os-nosdn-bar-ha.yml
    $ curl https://raw.githubusercontent.com/opnfv/compass4nfv/master/quickstart.sh | bash

Hardware configuration
----------------------
There's no specific Hardware configuration required.  However, the ``intel_rdt`` plugin works
only on platforms with Intel CPUs.

Feature configuration
---------------------
All Barometer plugins are automatically deployed on all compute nodes.  There is no option to
selectively install only a subset of plugins.  Any custom disabling or configuration must be done
directly on the compute node(s) after the deployment is completed.

Upgrading the plugins
---------------------
The Barometer components are built-in in the ISO image, and respectively the RPM/Debian packages.
There is no simple way to update only the Barometer plugins in an existing deployment.
