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

Platform components validation - Apex
-------------------------------------
The following steps describe how to perform a simple "manual" testing of the Barometer components:

On the controller:

1. Get a list of the available metrics:

   .. code::

      $ openstack metric list

2. Take note of the ID of the metric of interest, and show the measures of this metric:

   .. code::

      $ openstack metric measures show <metric_id>

3. Watch the measure list for updates to verify that metrics are being added:

   .. code:: bash

      $ watch –n2 –d openstack metric measures show <metric_id>

More on testing and displaying metrics is shown below.

On the compute:

1. Connect to any compute node and ensure that the collectd service is running.  The log file
   ``collectd.log`` should contain no errors and should indicate that each plugin was successfully
   loaded.  For example, from the Jump Host:

   .. code:: bash

       $ opnfv-util overcloud compute0
       $ ls /etc/collectd/collectd.conf.d/
       $ systemctl status collectd
       $ vi /opt/stack/collectd.log

   The following plugings should be found loaded:
   aodh, gnocchi, hugepages, intel_rdt, mcelog, ovs_events, ovs_stats, snmp, virt

2. On the compute node, induce an event monitored by the plugins; e.g. a corrected memory error:

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

3. Connect to the controller and query the monitoring services.  Make sure the overcloudrc.v3
   file has been copied to the controller (from the undercloud VM or from the Jump Host) in order
   to be able to authenticate for OpenStack services.

   .. code:: bash

      $ opnfv-util overcloud controller0
      $ su
      $ source overcloudrc.v3
      $ gnocchi metric list
      $ aodh alarm list

   The output for the gnocchi and aodh queries should be similar to the excerpts below:

   .. code:: bash

      +--------------------------------------+---------------------+------------------------------------------------------------------------------------------------------------+-----------+-------------+
      | id                                   | archive_policy/name | name                                                                                                       | unit      | resource_id |
      +--------------------------------------+---------------------+------------------------------------------------------------------------------------------------------------+-----------+-------------+
        [...]
      | 0550d7c1-384f-4129-83bc-03321b6ba157 | high                | overcloud-novacompute-0.jf.intel.com-hugepages-mm-2048Kb@vmpage_number.free                                | Pages     | None        |
      | 0cf9f871-0473-4059-9497-1fea96e5d83a | high                | overcloud-novacompute-0.jf.intel.com-hugepages-node0-2048Kb@vmpage_number.free                             | Pages     | None        |
      | 0d56472e-99d2-4a64-8652-81b990cd177a | high                | overcloud-novacompute-0.jf.intel.com-hugepages-node1-1048576Kb@vmpage_number.used                          | Pages     | None        |
      | 0ed71a49-6913-4e57-a475-d30ca2e8c3d2 | high                | overcloud-novacompute-0.jf.intel.com-hugepages-mm-1048576Kb@vmpage_number.used                             | Pages     | None        |
      | 11c7be53-b2c1-4c0e-bad7-3152d82c6503 | high                | overcloud-novacompute-0.jf.intel.com-mcelog-                                                               | None      | None        |
      |                                      |                     | SOCKET_0_CHANNEL_any_DIMM_any@errors.uncorrected_memory_errors_in_24h                                      |           |             |
      | 120752d4-385e-4153-aed8-458598a2a0e0 | high                | overcloud-novacompute-0.jf.intel.com-cpu-24@cpu.interrupt                                                  | jiffies   | None        |
      | 1213161e-472e-4e1b-9e56-5c6ad1647c69 | high                | overcloud-novacompute-0.jf.intel.com-cpu-6@cpu.softirq                                                     | jiffies   | None        |
        [...]

      +--------------------------------------+-------+------------------------------------------------------------------+-------+----------+---------+
      | alarm_id                             | type  | name                                                             | state | severity | enabled |
      +--------------------------------------+-------+------------------------------------------------------------------+-------+----------+---------+
      | fbd06539-45dd-42c5-a991-5c5dbf679730 | event | gauge.memory_erros(overcloud-novacompute-0.jf.intel.com-mcelog)  | ok    | moderate | True    |
      | d73251a5-1c4e-4f16-bd3d-377dd1e8cdbe | event | gauge.mcelog_status(overcloud-novacompute-0.jf.intel.com-mcelog) | ok    | moderate | True    |
        [...]


Platform components validation - Compass4nfv
--------------------------------------------

The procedure is similar to the above.

The following steps describe how to perform a simple "manual" testing of the Barometer components:

On the compute:

1. Connect to any compute node and ensure that the collectd service is running. The log file
   ``collectd.log`` should contain no errors and should indicate that each plugin was successfully
   loaded. For example, ssh into a compute node and test:

   .. code:: bash

       $ ls /etc/collectd/collectd.conf.d/
       $ systemctl status collectd
       $ vi /var/log/collectd.log

   The following plugings should be found loaded:
   aodh, gnocchi, hugepages, mcelog, ovs_events, ovs_stats, cpu, interface, memory, disk, numa, virt, rrdtool

2. Testing using mce-inject is similar to #2 shown above.

On the controller:

3. Connect to the controller and query the monitoring services. Make sure to log in to the lxc-utility
container before using the OpenStack CLI. Please refer to this wiki for details:
https://wiki.opnfv.org/display/compass4nfv/Containerized+Compass#ContainerizedCompass-HowtouseOpenStackCLI

   .. code:: bash

      $ source ~/openrc
      $ gnocchi metric list
      $ aodh alarm list

   The output for the gnocchi and aodh queries should be similar to the excerpts shown in #3 above.
