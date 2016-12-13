.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

collectd plugins
=================
Barometer has enabled the following collectd plugins:

* dpdkstat plugin: A read plugin that retrieve stats from the DPDK extended
   NIC stats API.

* `ceilometer plugin`_: A write plugin that pushes the retrieved stats to
  Ceilometer. It's capable of pushing any stats read through collectd to
  Ceilometer, not just the DPDK stats.

* hugepages plugin:  A read plugin that retrieves the number of available
  and free hugepages on a platform as well as what is available in terms of
  hugepages per socket.

* RDT plugin: A read plugin that provides the last level cache utilitzation and
  memory bandwidth utilization

* Open vSwitch events Plugin: A read plugin that retrieves events from OVS.

All the plugins above are available on the collectd master, except for the
ceilometer plugin as it's a python based plugin and only C plugins are accepted
by the collectd community. The ceilometer plugin lives in the OpenStack
repositories.

Other plugins under development or existing as a pull request into collectd master:

* dpdkevents:  A read plugin that retrieves DPDK link status and DPDK
  forwarding cores liveliness status (DPDK Keep Alive).

* Open vSwitch stats Plugin: A read plugin that retrieve flow and interface
  stats from OVS.

* mcelog plugin: A read plugin that uses mcelog client protocol to check for
  memory Machine Check Exceptions and sends the stats for reported exceptions.

* SNMP write: A write plugin that will act as a SNMP subagent and will map
  collectd metrics to relavent OIDs. Will only support SNMP: get, getnext and
  walk.

* Legacy/IPMI: A read plugin that will report platform thermals, voltages,
  fanspeed....

Building collectd with the Barometer plugins and installing the dependencies
=============================================================================

All plugins
-----------
The plugins that have been merged to the baromter master branch can all be
built and configured through the barometer repository.

**Note**: sudo permissions are required to install collectd.

**Note**: These are instructions for Ubuntu 16.04.

To build and install these dependencies, clone the barometer repo:

.. code:: c

    $ git clone https://gerrit.opnfv.org/gerrit/barometer

Install the build dependencies

.. code:: bash

    $ ./src/install_build_deps.sh

To install collectd as a service and install all it's dependencies:

.. code:: bash

    $ cd barometer/src && sudo make && sudo make install

This will install collectd as a service and the base install directory
is /opt/collectd.

Sample configuration files can be found in '/opt/collectd/etc/collectd.conf.d'

Please note if you are using any Open vSwitch plugins you need to run:

.. code:: bash

    $ sudo ovs-vsctl set-manager ptcp:6640

DPDK statistics plugin
-----------------------
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies: DPDK (http://dpdk.org/)

To build and install DPDK to /usr please see:
https://github.com/collectd/collectd/blob/master/docs/BUILD.dpdkstat.md

Building and installing collectd:

.. code:: bash

    $ git clone https://github.com/collectd/collectd.git
    $ cd collectd
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug
    $ make
    $ sudo make install


This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc
To configure the hugepages plugin you need to modify the configuration file to
include:

.. code:: bash

    LoadPlugin dpdkstat
    <Plugin dpdkstat>
           Coremask "0xf"
           ProcessType "secondary"
           FilePrefix "rte"
           EnabledPortMask 0xffff
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/collectd/collectd/blob/master/src/collectd.conf.pod

Please note if you are configuring collectd with the **static DPDK library**
you must compile the DPDK library with the -fPIC flag:

.. code:: bash

    $ make EXTRA_CFLAGS=-fPIC

You must also modify the configuration step when building collectd:

.. code:: bash

    $ ./configure CFLAGS=" -lpthread -Wl,--whole-archive -Wl,-ldpdk -Wl,-lm -Wl,-lrt -Wl,-lpcap -Wl,-ldl -Wl,--no-whole-archive"

Please also note that if you are not building and installing DPDK system-wide
you will need to specify the specific paths to the header files and libraries
using LIBDPDK_CPPFLAGS and LIBDPDK_LDFLAGS. You will also need to add the DPDK
library symbols to the shared library path using ldconfig. Note that this
update to the shared library path is not persistant (i.e. it will not survive a
reboot). Pending a merge of https://github.com/collectd/collectd/pull/2073.

.. code:: bash

    $ ./configure LIBDPDK_CPPFLAGS="path to DPDK header files" LIBDPDK_LDFLAGS="path to DPDK libraries"


Hugepages Plugin
-----------------
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies: None, but assumes hugepages are configured.

To configure some hugepages:

.. code:: bash

   sudo mkdir -p /mnt/huge
   sudo mount -t hugetlbfs nodev /mnt/huge
   sudo echo 14336 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

Building and installing collectd:

.. code:: bash

    $ git clone https://github.com/collectd/collectd.git
    $ cd collectd
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-hugepages --enable-debug
    $ make
    $ sudo make install

This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc
To configure the hugepages plugin you need to modify the configuration file to
include:

.. code:: bash

    LoadPlugin hugepages
    <Plugin hugepages>
        ReportPerNodeHP  true
        ReportRootHP     true
        ValuesPages      true
        ValuesBytes      false
        ValuesPercentage false
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/collectd/collectd/blob/master/src/collectd.conf.pod

Intel RDT Plugin
-----------------
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies:

  * PQoS/Intel RDT library https://github.com/01org/intel-cmt-cat.git
  * msr kernel module

Building and installing PQoS/Intel RDT library:

.. code:: bash

    $ git clone https://github.com/01org/intel-cmt-cat.git
    $ cd intel-cmt-cat.git
    $ make
    $ make install PREFIX=/usr

Building and installing collectd:

.. code:: bash

    $ git clone https://github.com/collectd/collectd.git
    $ cd collectd
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --with-libpqos=/usr/ --enable-debug
    $ make
    $ sudo make install

This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc
To configure the RDT plugin you need to modify the configuration file to
include:

.. code:: bash

    <LoadPlugin intel_rdt>
      Interval 1
    </LoadPlugin>
    <Plugin "intel_rdt">
      Cores ""
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/collectd/collectd/blob/master/src/collectd.conf.pod

Installing collectd as a service
--------------------------------
Collectd service scripts are available in the collectd/contrib directory.
To install collectd as a service:

.. code:: bash

    $ sudo cp contrib/systemd.collectd.service /etc/systemd/system/
    $ cd /etc/systemd/system/
    $ sudo mv systemd.collectd.service collectd.service
    $ sudo chmod +x collectd.service

Modify collectd.service

.. code:: bash

    [Service]
    ExecStart=/opt/collectd/sbin/collectd
    EnvironmentFile=-/opt/collectd/etc/
    EnvironmentFile=-/opt/collectd/etc/
    CapabilityBoundingSet=CAP_SETUID CAP_SETGID

Reload

.. code:: bash

    $ sudo systemctl daemon-reload
    $ sudo systemctl start collectd.service
    $ sudo systemctl status collectd.service should show success

Additional useful plugins
--------------------------

Exec Plugin
~~~~~~~~~~~

Can be used to show you when notifications are being generated by calling a
bash script that dumps notifications to file. (handy for debug). Modify
/opt/collectd/etc/collectd.conf:

.. code:: bash

   LoadPlugin exec
   <Plugin exec>
   #   Exec "user:group" "/path/to/exec"
      NotificationExec "user" "<path to barometer>/barometer/src/collectd/collectd_sample_configs/write_notification.sh"
   </Plugin>

write_notification.sh (just writes the notification passed from exec through
STDIN to a file (/tmp/notifications)):

.. code:: bash

   #!/bin/bash
   rm -f /tmp/notifications
   while read x y
   do
     echo $x$y >> /tmp/notifications
   done

output to /tmp/notifications should look like:

.. code:: bash

    Severity:WARNING
    Time:1479991318.806
    Host:localhost
    Plugin:ovs_events
    PluginInstance:br-ex
    Type:gauge
    TypeInstance:link_status
    uuid:f2aafeec-fa98-4e76-aec5-18ae9fc74589

    linkstate of "br-ex" interface has been changed to "DOWN"

logfile plugin
~~~~~~~~~~~~~~~
Can be used to log collectd activity. Modify /opt/collectd/etc/collectd.conf to
include:

.. code:: bash

    LoadPlugin logfile
    <Plugin logfile>
        LogLevel info
        File "/var/log/collectd.log"
        Timestamp true
        PrintSeverity false
    </Plugin>

Monitoring Interfaces and Openstack Support
-------------------------------------------
.. Figure:: monitoring_interfaces.png

   Monitoring Interfaces and Openstack Support

The figure above shows the DPDK L2 forwarding application running on a compute
node, sending and receiving traffic. collectd is also running on this compute
node retrieving the stats periodically from DPDK through the dpdkstat plugin
and publishing the retrieved stats to Ceilometer through the ceilometer plugin.

To see this demo in action please checkout: `Barometer OPNFV Summit demo`_

References
----------
[1] https://collectd.org/wiki/index.php/Naming_schema
[2] https://github.com/collectd/collectd/blob/master/src/daemon/plugin.h
[3] https://collectd.org/wiki/index.php/Value_list_t
[4] https://collectd.org/wiki/index.php/Data_set
[5] https://collectd.org/documentation/manpages/types.db.5.shtml
[6] https://collectd.org/wiki/index.php/Data_source
[7] https://collectd.org/wiki/index.php/Meta_Data_Interface

.. _Barometer OPNFV Summit demo: https://prezi.com/kjv6o8ixs6se/software-fastpath-service-quality-metrics-demo/
.. _ceilometer plugin: https://github.com/openstack/collectd-ceilometer-plugin/tree/stable/mitaka
