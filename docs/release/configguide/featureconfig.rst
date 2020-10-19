.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=============================
Barometer Configuration Guide
=============================
This document provides guidelines on how to install and configure Barometer with Apex and Compass4nfv.
The deployment script installs and enables a series of collectd plugins on the compute node(s),
which collect and dispatch specific metrics and events from the platform.

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
