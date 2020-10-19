.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================================
Barometer post installation procedures
======================================
This document describes briefly the methods of validating the Barometer installation.

Automated post installation activities
--------------------------------------
The Barometer test-suite in Functest is called ``barometercollectd`` and is part of the ``Features``
tier.  Running these tests is done automatically by the OPNFV deployment pipeline on the supported
scenarios.  The testing consists of basic verifications that each plugin is functional per their
default configurations.  Inside the Functest container, the detailed results can be found in the
``/home/opnfv/functest/results/barometercollectd.log``.

Barometer post configuration procedures
---------------------------------------
The functionality for each plugin (such as enabling/disabling and configuring its capabilities)
is controlled as described in the User Guide through their individual ``.conf`` file located in
the ``/etc/collectd/collectd.conf.d/`` folder on the compute node(s).  In order for any changes to
take effect, the collectd service must be stopped and then started again.

