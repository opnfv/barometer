.. _barometer-postinstall:

.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

======================================
Barometer post installation procedures
======================================
This document describes briefly the methods of validating the Barometer installation.

.. TODO: Update this to include reference to containers rather than an Openstack deployment.

Automated post installation activities
--------------------------------------
.. This section will include how to run plugin validation tests, when they are created/merged.
.. This section will also include some troubleshooting and debugging information.

.. note:: This section is outdated and needs to be updated.

.. TODO: Update this section; post-installation/verification shouldn't be in
   the config guide. It should be in testing.

The Barometer test-suite in Functest is called ``barometercollectd`` and is part of the ``Features``
tier.  Running these tests is done automatically by the OPNFV deployment pipeline on the supported
scenarios.  The testing consists of basic verifications that each plugin is functional per their
default configurations.  Inside the Functest container, the detailed results can be found in the
``/home/opnfv/functest/results/barometercollectd.log``.

Barometer post configuration procedures
---------------------------------------
The functionality for each plugin (such as enabling/disabling and configuring its capabilities)
is controlled as described in the :ref:`User Guide <barometer-userguide>` through their individual
``.conf`` file located in the ``/etc/collectd/collectd.conf.d/`` on the host(s). In order for any
changes to take effect, the collectd service must be stopped and then started again.

Plugin verification
~~~~~~~~~~~~~~~~~~~
Once collectd has been installed and deployed, you will see metrics from most plugins immediately. However, in some cases, you may want to verify that the configuration is correct and that the plugion is functioning as intended (particularly during development, or when testing an experimental version). The following sections provide some verification steps to make sure the plugins are working as expected.

MCElog
^^^^^^
On the collectd host, you can induce an event monitored by the plugins; e.g. a corrected memory error:

.. code:: bash

   $ git clone https://git.kernel.org/pub/scm/utils/cpu/mce/mce-inject.git
   $ cd mce-inject
   $ make
   $ modprobe mce-inject

Modify the test/corrected script to include the following:

.. code:: bash

   CPU 0 BANK 0
   STATUS 0xcc00008000010090
   ADDR 0x0010FFFFFFF

Inject the error:

.. code:: bash

   $ ./mce-inject < test/corrected

.. TODO: How to check that the event was propogated to collectd

.. _barometer-docker-verification:

Barometer post installation verification on barometer-collectd container
------------------------------------------------------------------------

The following steps describe how to perform simple "manual" testing of the Barometer components
after :ref:`successfully deploying the barometer-collectd container<barometer-docker-userguide>`:

1. Connect to any compute node and ensure that the collectd container is running.

   .. code:: bash

       root@host2:~# docker ps | grep collectd

   You should see the container ``opnfv/barometer-collectd`` running.

2. Use a web browser to connect to Grafana at ``http://<serverip>:3000/``, using the hostname or
   IP of your server and port 3000. Log in with admin/admin. You will see ``collectd``
   InfluxDB database in the ``Data Sources``. Also, you will notice metrics coming in the several
   dashboards such as ``CPU Usage`` and ``Host Overview``.

For more details on the Barometer containers, Grafana and InfluxDB, please refer to
the following documentation links:

`Barometer Containers wiki page <https://wiki.opnfv.org/display/fastpath/Barometer+Containers#BarometerContainers-barometer-collectdcontainer>`_

:ref:`Barometer Docker install guide<barometer-docker-userguide>`
