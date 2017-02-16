.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

========================
Barometer Configuration
========================
This document provides guidelines on how to install and configure the Barometer
plugin when using Fuel as a deployment tool. The plugin name is: Collectd
Ceilometer Plugin. This plugin installs collectd on a compute node and enables
a number of collectd plugins to collect metrics and events from the platform
and send them to ceilometer.

.. contents::
   :depth: 3
   :local:

Pre-configuration activities
----------------------------
The Barometer Fuel plugin can be found in /opt/opnfv on the fuel master.
To enable this plugin:

.. code:: bash

    $ cd /opt/opnfv
    $ fuel plugins --install fuel-plugin-collectd-ceilometer-1.0-1.0.0-1.noarch.rpm

On the Fuel UI, create a new environment.
* In Settings > OpenStack Services
* Enable "Install Ceilometer and Aodh"
* In Settings > Other
* Enable "Deploy Collectd Ceilometer Plugin"
* Enable the barometer plugins you'd like to deploy using the checkboxes
* Continue with environment configuration and deployment as normal.

Hardware configuration
----------------------
There's no specific Hardware configuration required for this the barometer fuel plugin.

Feature configuration
---------------------
Describe the procedures to configure your feature on the platform in order
that it is ready to use according to the feature instructions in the platform
user guide.  Where applicable you should add content in the postinstall.rst
to validate the feature is configured for use.
(checking components are installed correctly etc...)

Upgrading the plugin
--------------------

From time to time new versions of the plugin may become available.

The plugin cannot be upgraded if an active environment is using the plugin.

In order to upgrade the plugin:

* Copy the updated plugin file to the fuel-master.
* On the Fuel UI, reset the environment.
* On the Fuel CLI "fuel plugins --update <fuel-plugin-file>"
* On the Fuel UI, re-deploy the environment.

