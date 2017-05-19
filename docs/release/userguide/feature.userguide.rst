.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV Barometer User Guide
===================================

.. contents::
   :depth: 3
   :local:

Barometer collectd plugins description
---------------------------------------
.. Describe the specific features and how it is realised in the scenario in a brief manner
.. to ensure the user understand the context for the user guide instructions to follow.

collectd is a daemon which collects system performance statistics periodically
and provides a variety of mechanisms to publish the collected metrics. It
supports more than 90 different input and output plugins. Input plugins
retrieve metrics and publish them to the collectd deamon, while output plugins
publish the data they receive to an end point. collectd also has infrastructure
to support thresholding and notification.

Barometer has enabled the following collectd plugins:

* *dpdkstat plugin*: A read plugin that retrieve stats from the DPDK extended
   NIC stats API.

* *dpdkevents plugin*:  A read plugin that retrieves DPDK link status and DPDK
  forwarding cores liveliness status (DPDK Keep Alive).

* `ceilometer plugin`_: A write plugin that pushes the retrieved stats to
  Ceilometer. It's capable of pushing any stats read through collectd to
  Ceilometer, not just the DPDK stats.

* *hugepages plugin*:  A read plugin that retrieves the number of available
  and free hugepages on a platform as well as what is available in terms of
  hugepages per socket.

* *Open vSwitch events Plugin*: A read plugin that retrieves events from OVS.

* *Open vSwitch stats Plugin*: A read plugin that retrieves flow and interface
  stats from OVS.

* *mcelog plugin*: A read plugin that uses mcelog client protocol to check for
  memory Machine Check Exceptions and sends the stats for reported exceptions

* *RDT plugin*: A read plugin that provides the last level cache utilization and
  memory bandwidth utilization

All the plugins above are available on the collectd master, except for the
ceilometer plugin as it's a python based plugin and only C plugins are accepted
by the collectd community. The ceilometer plugin lives in the OpenStack
repositories.

Other plugins existing as a pull request into collectd master:

* *SNMP Agent*: A write plugin that will act as a AgentX subagent that receives
  and handles queries from SNMP master agent and returns the data collected
  by read plugins. The SNMP Agent plugin handles requests only for OIDs
  specified in configuration file. To handle SNMP queries the plugin gets data
  from collectd and translates requested values from collectd's internal format
  to SNMP format. Supports SNMP: get, getnext and walk requests.

* *Legacy/IPMI*: A read plugin that reports platform thermals, voltages,
  fanspeed, current, flow, power etc. Also, the plugin monitors Intelligent
  Platform Management Interface (IPMI) System Event Log (SEL) and sends the

* *virt*: A read plugin that uses virtualization API *libvirt* to gather
  statistics about virtualized guests on a system directly from the hypervisor,
  without a need to install collectd instance on the guest.

**Plugins included in the Danube release:**

* Hugepages
* Open vSwitch Events
* Ceilometer
* Mcelog

collectd capabilities and usage
------------------------------------
.. Describe the specific capabilities and usage for <XYZ> feature.
.. Provide enough information that a user will be able to operate the feature on a deployed scenario.

.. note:: Plugins included in the OPNFV D release will be built-in to the fuel
 plugin and available in the /opt/opnfv directory on the fuel master. You don't
 need to clone the barometer/collectd repos to use these, but you can configure
 them as shown in the examples below.

 The collectd plugins in OPNFV are configured with reasonable defaults, but can
 be overridden.

Building all Barometer upstreamed plugins from scratch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The plugins that have been merged to the collectd master branch can all be
built and configured through the barometer repository.

.. note::
 * sudo permissions are required to install collectd.
 * These are instructions for Ubuntu 16.04

To build all the upstream plugins, clone the barometer repo:

.. code:: c

    $ git clone https://gerrit.opnfv.org/gerrit/barometer

To install collectd as a service and install all it's dependencies:

.. code:: bash

    $ cd barometer && ./systems/build_base_machine.sh

This will install collectd as a service and the base install directory
will be /opt/collectd.

Sample configuration files can be found in '/opt/collectd/etc/collectd.conf.d'

.. note::
  - If you plan on using the Exec plugin, the plugin requires non-root
    user to execute scripts. By default, `collectd_exec` user is used. Barometer
    scripts do *not* create this user. It needs to be manually added or exec plugin
    configuration has to be changed to use other, existing user before starting
    collectd service.

  - If you don't want to use one of the Barometer plugins, simply remove the
    sample config file from '/opt/collectd/etc/collectd.conf.d'

  - If you are using any Open vSwitch plugins you need to run:

.. code:: bash

    $ sudo ovs-vsctl set-manager ptcp:6640


Below is the per plugin installation and configuration guide, if you only want
to install some/particular plugins.

DPDK plugins
^^^^^^^^^^^^^
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies: DPDK (http://dpdk.org/)

.. note:: DPDK statistics plugin requires DPDK version 16.04 or later

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

.. note:: If DPDK was installed in a non standard location you will need to
    specify paths to the header files and libraries using *LIBDPDK_CPPFLAGS* and
    *LIBDPDK_LDFLAGS*. You will also need to add the DPDK library symbols to the
    shared library path using *ldconfig*. Note that this update to the shared
    library path is not persistant (i.e. it will not survive a reboot).

Example of specifying custom paths to DPDK headers and libraries:

.. code:: bash

    $ ./configure LIBDPDK_CPPFLAGS="path to DPDK header files" LIBDPDK_LDFLAGS="path to DPDK libraries"

This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc

To configure the dpdkstats plugin you need to modify the configuration file to
include:

.. code:: bash

    LoadPlugin dpdkstat
    <Plugin "dpdkstat">
        <EAL>
            Coremask "0x2"
            MemoryChannels "4"
            ProcessType "secondary"
            FilePrefix "rte"
        </EAL>
        EnabledPortMask 0xffff
        PortName "interface1"
        PortName "interface2"
    </Plugin>


To configure the dpdkevents plugin you need to modify the configuration file to
include:

.. code:: bash

    LoadPlugin dpdkevents
    <Plugin "dpdkevents">
        Interval 1
        <EAL>
            Coremask "0x1"
            MemoryChannels "4"
            ProcessType "secondary"
            FilePrefix "rte"
        </EAL>
        <Event "link_status">
            SendEventsOnUpdate true
            EnabledPortMask 0xffff
            PortName "interface1"
            PortName "interface2"
            SendNotification false
        </Event>
        <Event "keep_alive">
            SendEventsOnUpdate true
            LCoreMask "0xf"
            KeepAliveShmName "/dpdk_keepalive_shm_name"
            SendNotification false
        </Event>
    </Plugin>

.. note:: Currently, the DPDK library doesn’t support API to de-initialize
 the DPDK resources allocated on the initialization. It means, the collectd
 plugin will not be able to release the allocated DPDK resources
 (locks/memory/pci bindings etc.) correctly on collectd shutdown or reinitialize
 the DPDK library if primary DPDK process is restarted. The only way to release
 those resources is to terminate the process itself. For this reason, the plugin
 forks off a separate collectd process. This child process becomes a secondary
 DPDK process which can be run on specific CPU cores configured by user through
 collectd configuration file (“Coremask” EAL configuration option, the
 hexadecimal bitmask of the cores to run on).

For more information on the plugin parameters, please see:
https://github.com/collectd/collectd/blob/master/src/collectd.conf.pod

.. note:: dpdkstat plugin initialization time depends on read interval. It
 requires 5 read cycles to set up internal buffers and states. During that time
 no statistics are submitted. Also if plugin is running and the number of DPDK
 ports is increased, internal buffers are resized. That requires 3 read cycles
 and no port statistics are submitted in that time.

The Address-Space Layout Randomization (ASLR) security feature in Linux should be
disabled, in order for the same hugepage memory mappings to be present in all
DPDK multi-process applications.

To disable ASLR:

.. code:: bash

    $ sudo echo 0 > /proc/sys/kernel/randomize_va_space

To fully enable ASLR:

.. code:: bash

    $ sudo echo 2 > /proc/sys/kernel/randomize_va_space

.. warning:: Disabling Address-Space Layout Randomization (ASLR) may have security
    implications. It is recommended to be disabled only when absolutely necessary,
    and only when all implications of this change have been understood.

For more information on multi-process support, please see:
http://dpdk.org/doc/guides/prog_guide/multi_proc_support.html

**DPDK stats plugin limitations:**

1. The DPDK primary process application should use the same version of DPDK
   that collectd DPDK plugin is using;

2. L2 statistics are only supported;

3. The plugin has been tested on Intel NIC’s only.

**DPDK stats known issues:**

* DPDK port visibility

  When network port controlled by Linux is bound to DPDK driver, the port
  will not be available in the OS. It affects the SNMP write plugin as those
  ports will not be present in standard IF-MIB. Thus addition work is
  required to be done to support DPDK ports and statistics.

Hugepages Plugin
^^^^^^^^^^^^^^^^^
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
^^^^^^^^^^^^^^^^
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies:

  * PQoS/Intel RDT library https://github.com/01org/intel-cmt-cat.git
  * msr kernel module

Building and installing PQoS/Intel RDT library:

.. code:: bash

    $ git clone https://github.com/01org/intel-cmt-cat.git
    $ cd intel-cmt-cat
    $ make
    $ make install PREFIX=/usr

You will need to insert the msr kernel module:

.. code:: bash

    $ modprobe msr

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

IPMI Plugin
^^^^^^^^^^^^
Repo: https://github.com/maryamtahhan/collectd

Branch: feat_ipmi_events, feat_ipmi_analog

Dependencies: OpenIPMI library (http://openipmi.sourceforge.net/)

The IPMI plugin is already implemented in the latest collectd and sensors
like temperature, voltage, fanspeed, current are already supported there.
The list of supported IPMI sensors has been extended and sensors like flow,
power are supported now. Also, a System Event Log (SEL) notification feature
has been introduced.

* The feat_ipmi_events branch includes new SEL feature support in collectd
  IPMI plugin. If this feature is enabled, the collectd IPMI plugin will
  dispatch notifications about new events in System Event Log.

* The feat_ipmi_analog branch includes the support of extended IPMI sensors in
  collectd IPMI plugin.

**Install dependencies**

On Ubuntu, the OpenIPMI library can be installed via apt package manager:

.. code:: bash

    $ sudo apt-get install libopenipmi-dev

Anyway, it's recommended to use the latest version of the OpenIPMI library as
it includes fixes of known issues which aren't included in standard OpenIPMI
library package. The latest version of the library can be found at
https://sourceforge.net/p/openipmi/code/ci/master/tree/. Steps to install the
library from sources are described below.

Remove old version of OpenIPMI library:

.. code:: bash

    $ sudo apt-get remove libopenipmi-dev

Download OpenIPMI library sources:

.. code:: bash

    $ git clone https://git.code.sf.net/p/openipmi/code openipmi-code
    $ cd openipmi-code

Patch the OpenIPMI pkg-config file to provide correct compilation flags
for collectd IPMI plugin:

.. code:: diff

    diff --git a/OpenIPMIpthread.pc.in b/OpenIPMIpthread.pc.in
    index 59b52e5..fffa0d0 100644
    --- a/OpenIPMIpthread.pc.in
    +++ b/OpenIPMIpthread.pc.in
    @@ -6,6 +6,6 @@ includedir=@includedir@
     Name: OpenIPMIpthread
     Description: Pthread OS handler for OpenIPMI
     Version: @VERSION@
    -Requires: OpenIPMI pthread
    +Requires: OpenIPMI
     Libs: -L${libdir} -lOpenIPMIutils -lOpenIPMIpthread
    -Cflags: -I${includedir}
    +Cflags: -I${includedir} -pthread

Build and install OpenIPMI library:

.. code:: bash

    $ autoreconf --install
    $ ./configure --prefix=/usr
    $ make
    $ sudo make install

Enable IPMI support in the kernel:

.. code:: bash

    $ sudo modprobe ipmi_devintf
    $ sudo modprobe ipmi_si

**Note**: If HW supports IPMI, the ``/dev/ipmi0`` character device will be
created.

Clone and install the collectd IPMI plugin:

.. code:: bash

    $ git clone  https://github.com/maryamtahhan/collectd
    $ cd collectd
    $ git checkout $BRANCH
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug
    $ make
    $ sudo make install

Where $BRANCH is feat_ipmi_events or feat_ipmi_analog.

This will install collectd to default folder ``/opt/collectd``. The collectd
configuration file (``collectd.conf``) can be found at ``/opt/collectd/etc``. To
configure the IPMI plugin you need to modify the file to include:

.. code:: bash

    LoadPlugin ipmi
    <Plugin ipmi>
       SELEnabled true # only feat_ipmi_events branch supports this
    </Plugin>

**Note**: By default, IPMI plugin will read all available analog sensor values,
dispatch the values to collectd and send SEL notifications.

For more information on the IPMI plugin parameters and SEL feature configuration,
please see:
https://github.com/maryamtahhan/collectd/blob/feat_ipmi_events/src/collectd.conf.pod

Extended analog sensors support doesn't require additional configuration. The usual
collectd IPMI documentation can be used:

- https://collectd.org/wiki/index.php/Plugin:IPMI
- https://collectd.org/documentation/manpages/collectd.conf.5.shtml#plugin_ipmi

IPMI documentation:

- https://www.kernel.org/doc/Documentation/IPMI.txt
- http://www.intel.com/content/www/us/en/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html

Mcelog Plugin
^^^^^^^^^^^^^^
Repo: https://github.com/collectd/collectd

Branch: master

Dependencies: mcelog

Start by installing mcelog. Note: The kernel has to have CONFIG_X86_MCE
enabled. For 32bit kernels you need at least a 2.6,30 kernel.

On ubuntu:

.. code:: bash

    $ apt-get update && apt-get install mcelog

Or build from source

.. code:: bash

    $ git clone git://git.kernel.org/pub/scm/utils/cpu/mce/mcelog.git
    $ cd mcelog
    $ make
    ... become root ...
    $ make install
    $ cp mcelog.service /etc/systemd/system/
    $ systemctl enable mcelog.service
    $ systemctl start mcelog.service


Verify you got a /dev/mcelog. You can verify the daemon is running completely
by running:

.. code:: bash

     $ mcelog --client

This should query the information in the running daemon. If it prints nothing
that is fine (no errors logged yet). More info @
http://www.mcelog.org/installation.html

Modify the mcelog configuration file "/etc/mcelog/mcelog.conf" to include or
enable:

.. code:: bash

    socket-path = /var/run/mcelog-client

Clone and install the collectd mcelog plugin:

.. code:: bash

    $ git clone  https://github.com/maryamtahhan/collectd
    $ cd collectd
    $ git checkout feat_ras
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug
    $ make
    $ sudo make install

This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc
To configure the mcelog plugin you need to modify the configuration file to
include:

.. code:: bash

    <LoadPlugin mcelog>
      Interval 1
    </LoadPlugin>
    <Plugin "mcelog">
       McelogClientSocket "/var/run/mcelog-client"
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/maryamtahhan/collectd/blob/feat_ras/src/collectd.conf.pod

Simulating a Machine Check Exception can be done in one of 3 ways:

* Running $make test in the mcelog cloned directory - mcelog test suite
* using mce-inject
* using mce-test

**mcelog test suite:**

It is always a good idea to test an error handling mechanism before it is
really needed. mcelog includes a test suite. The test suite relies on
mce-inject which needs to be installed and in $PATH.

You also need the mce-inject kernel module configured (with
CONFIG_X86_MCE_INJECT=y), compiled, installed and loaded:

.. code:: bash

    $ modprobe mce-inject

Then you can run the mcelog test suite with

.. code:: bash

    $ make test

This will inject different classes of errors and check that the mcelog triggers
runs. There will be some kernel messages about page offlining attempts. The
test will also lose a few pages of memory in your system (not significant)
**Note this test will kill any running mcelog, which needs to be restarted
manually afterwards**.
**mce-inject:**

A utility to inject corrected, uncorrected and fatal machine check exceptions

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

**Note: the uncorrected and fatal scripts under test will cause a platform reset.
Only the fatal script generates the memory errors**. In order to  quickly
emulate uncorrected memory errors and avoid host reboot following test errors
from mce-test  suite can be injected:

.. code:: bash

       $ mce-inject  mce-test/cases/coverage/soft-inj/recoverable_ucr/data/srao_mem_scrub

**mce-test:**

In addition an more in-depth test of the Linux kernel machine check facilities
can be done with the mce-test test suite. mce-test supports testing uncorrected
error handling, real error injection, handling of different soft offlining
cases, and other tests.

**Corrected memory error injection:**

To inject corrected memory errors:

* Remove sb_edac and edac_core kernel modules: rmmod sb_edac rmmod edac_core
* Insert einj module: modprobe einj param_extension=1
* Inject an error by specifying details (last command should be repeated at least two times):

.. code:: bash

    $ APEI_IF=/sys/kernel/debug/apei/einj
    $ echo 0x8 > $APEI_IF/error_type
    $ echo 0x01f5591000 > $APEI_IF/param1
    $ echo 0xfffffffffffff000 > $APEI_IF/param2
    $ echo 1 > $APEI_IF/notrigger
    $ echo 1 > $APEI_IF/error_inject

* Check the MCE statistic: mcelog --client. Check the mcelog log for injected error details: less /var/log/mcelog.

Open vSwitch Plugins
^^^^^^^^^^^^^^^^^^^^^
OvS Plugins Repo: https://github.com/collectd/collectd

OvS Plugins Branch: master

OvS Events MIBs: The SNMP OVS interface link status is provided by standard
IF-MIB (http://www.net-snmp.org/docs/mibs/IF-MIB.txt)

Dependencies: Open vSwitch, Yet Another JSON Library (https://github.com/lloyd/yajl)

On Ubuntu, install the dependencies:

.. code:: bash

    $ sudo apt-get install libyajl-dev openvswitch-switch

Start the Open vSwitch service:

.. code:: bash

    $ sudo service openvswitch-switch start

configure the ovsdb-server manager:

.. code:: bash

    $ sudo ovs-vsctl set-manager ptcp:6640

Clone and install the collectd ovs plugin:

.. code:: bash

    $ git clone $REPO
    $ cd collectd
    $ git checkout master
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug
    $ make
    $ sudo make install

This will install collectd to /opt/collectd. The collectd configuration file
can be found at /opt/collectd/etc. To configure the OVS events plugin you
need to modify the configuration file to include:

.. code:: bash

    <LoadPlugin ovs_events>
       Interval 1
    </LoadPlugin>
    <Plugin "ovs_events">
       Port 6640
       Socket "/var/run/openvswitch/db.sock"
       Interfaces "br0" "veth0"
       SendNotification false
       DispatchValues true
    </Plugin>

To configure the OVS stats plugin you need to modify the configuration file
to include:

.. code:: bash

    <LoadPlugin ovs_stats>
       Interval 1
    </LoadPlugin>
    <Plugin ovs_stats>
       Port "6640"
       Address "127.0.0.1"
       Socket "/var/run/openvswitch/db.sock"
       Bridges "br0" "br_ext"
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/collectd/collectd/blob/master/src/collectd.conf.pod

SNMP Agent Plugin
^^^^^^^^^^^^^^^^^
Repo: https://github.com/maryamtahhan/collectd/

Branch: feat_snmp

Dependencies: NET-SNMP library

Start by installing net-snmp and dependencies.

On ubuntu:

.. code:: bash

    $ apt-get install snmp snmp-mibs-downloader snmpd libsnmp-dev
    $ systemctl start snmpd.service

Or build from source

Become root to install net-snmp dependencies

.. code:: bash

    $ apt-get install libperl-dev

Clone and build net-snmp

.. code:: bash

    $ git clone https://github.com/haad/net-snmp.git
    $ cd net-snmp
    $ ./configure --with-persistent-directory="/var/net-snmp" --with-systemd --enable-shared --prefix=/usr
    $ make

Become root

.. code:: bash

    $ make install

Copy default configuration to persistent folder

.. code:: bash

    $ cp EXAMPLE.conf /usr/share/snmp/snmpd.conf

Set library path and default MIB configuration

.. code:: bash

    $ cd ~/
    $ echo export LD_LIBRARY_PATH=/usr/lib >> .bashrc
    $ net-snmp-config --default-mibdirs
    $ net-snmp-config --snmpconfpath

Configure snmpd as a service

.. code:: bash

    $ cd net-snmp
    $ cp ./dist/snmpd.service /etc/systemd/system/
    $ systemctl enable snmpd.service
    $ systemctl start snmpd.service

Add the following line to snmpd.conf configuration file
"/usr/share/snmp/snmpd.conf" to make all OID tree visible for SNMP clients:

.. code:: bash

    view   systemonly  included   .1

To verify that SNMP is working you can get IF-MIB table using SNMP client
to view the list of Linux interfaces:

.. code:: bash

    $ snmpwalk -v 2c -c public localhost IF-MIB::interfaces

Clone and install the collectd snmp_agent plugin:

.. code:: bash

    $ git clone  https://github.com/maryamtahhan/collectd
    $ cd collectd
    $ git checkout feat_snmp
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug --enable-snmp --with-libnetsnmp
    $ make
    $ sudo make install

This will install collectd to /opt/collectd
The collectd configuration file can be found at /opt/collectd/etc
**SNMP Agent plugin is a generic plugin and cannot work without configuration**.
To configure the snmp_agent plugin you need to modify the configuration file to
include OIDs mapped to collectd types. The following example maps scalar
memAvailReal OID to value represented as free memory type of memory plugin:

.. code:: bash

    LoadPlugin snmp_agent
    <Plugin "snmp_agent">
      <Data "memAvailReal">
        Plugin "memory"
        Type "memory"
        TypeInstance "free"
        OIDs "1.3.6.1.4.1.2021.4.6.0"
      </Data>
    </Plugin>

**Limitations**

* Object instance with Counter64 type is not supported in SNMPv1. When GetNext
  request is received, Counter64 type objects will be skipped. When Get
  request is received for Counter64 type object, the error will be returned.
* Interfaces that are not visible to Linux like DPDK interfaces cannot be
  retreived using standard IF-MIB tables.

For more information on the plugin parameters, please see:
https://github.com/maryamtahhan/collectd/blob/feat_snmp/src/collectd.conf.pod

For more details on AgentX subagent, please see:
http://www.net-snmp.org/tutorial/tutorial-5/toolkit/demon/

virt plugin
^^^^^^^^^^^^
Repo: https://github.com/maryamtahhan/collectd

Branch: feat_libvirt_upstream

Dependencies: libvirt (https://libvirt.org/), libxml2

On Ubuntu, install the dependencies:

.. code:: bash

    $ sudo apt-get install libxml2-dev

Install libvirt:

libvirt version in package manager might be quite old and offer only limited
functionality. Hence, building and installing libvirt from sources is recommended.
Detailed instructions can bet found at:
https://libvirt.org/compiling.html

Certain metrics provided by the plugin have a requirement on a minimal version of
the libvirt API. *File system information* statistics require a *Guest Agent (GA)*
to be installed and configured in a VM. User must make sure that installed GA
version supports retrieving file system information. Number of *Performance monitoring events*
metrics depends on running libvirt daemon version.

.. note:: Please keep in mind that RDT metrics (part of *Performance monitoring
    events*) have to be supported by hardware. For more details on hardware support,
    please see:
    https://github.com/01org/intel-cmt-cat

    Additionally perf metrics **cannot** be collected if *Intel RDT* plugin is enabled.

libvirt version can be checked with following commands:

.. code:: bash

    $ virsh --version
    $ libvirtd --version

.. table:: Extended statistics requirements

    +-------------------------------+--------------------------+-------------+
    | Statistic                     | Min. libvirt API version | Requires GA |
    +===============================+==========================+=============+
    | Domain reason                 | 0.9.2                    | No          |
    +-------------------------------+--------------------------+-------------+
    | Disk errors                   | 0.9.10                   | No          |
    +-------------------------------+--------------------------+-------------+
    | Job statistics                | 1.2.9                    | No          |
    +-------------------------------+--------------------------+-------------+
    | File system information       | 1.2.11                   | Yes         |
    +-------------------------------+--------------------------+-------------+
    | Performance monitoring events | 1.3.3                    | No          |
    +-------------------------------+--------------------------+-------------+

Start libvirt daemon:

.. code:: bash

    $ systemctl start libvirtd

Create domain (VM) XML configuration file. For more information on domain XML
format and examples, please see:
https://libvirt.org/formatdomain.html

.. note:: Installing additional hypervisor dependencies might be required before
    deploying virtual machine.

Create domain, based on created XML file:

.. code:: bash

    $ virsh define DOMAIN_CFG_FILE.xml

Start domain:

.. code:: bash

    $ virsh start DOMAIN_NAME

Check if domain is running:

.. code:: bash

    $ virsh list

Check list of available *Performance monitoring events* and their settings:

.. code:: bash

    $ virsh perf DOMAIN_NAME

Enable or disable *Performance monitoring events* for domain:

.. code:: bash

    $ virsh perf DOMAIN_NAME [--enable | --disable] EVENT_NAME --live

Clone and install the collectd virt plugin:

.. code:: bash

    $ git clone $REPO
    $ cd collectd
    $ git checkout $BRANCH
    $ ./build.sh
    $ ./configure --enable-syslog --enable-logfile --enable-debug
    $ make
    $ sudo make install

Where ``$REPO`` and ``$BRANCH`` are equal to information provided above.

This will install collectd to ``/opt/collectd``. The collectd configuration file
``collectd.conf`` can be found at ``/opt/collectd/etc``. To load the virt plugin
user needs to modify the configuration file to include:

.. code:: bash

    LoadPlugin virt

Additionally, user can specify plugin configuration parameters in this file,
such as connection URI, domain name and much more. By default extended virt plugin
statistics are disabled. They can be enabled with ``ExtraStats`` option.

.. code:: bash

    <Plugin virt>
       RefreshInterval 60
       ExtraStats "cpu_util disk disk_err domain_state fs_info job_stats_background pcpu perf vcpupin"
    </Plugin>

For more information on the plugin parameters, please see:
https://github.com/maryamtahhan/collectd/blob/feat_libvirt_upstream/src/collectd.conf.pod

Installing collectd as a service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**NOTE**: In an OPNFV installation, collectd is installed and configured as a
service.

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
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Exec Plugin** : Can be used to show you when notifications are being
 generated by calling a bash script that dumps notifications to file. (handy
 for debug). Modify /opt/collectd/etc/collectd.conf:

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

* **logfile plugin**: Can be used to log collectd activity. Modify
  /opt/collectd/etc/collectd.conf to include:

.. code:: bash

    LoadPlugin logfile
    <Plugin logfile>
        LogLevel info
        File "/var/log/collectd.log"
        Timestamp true
        PrintSeverity false
    </Plugin>


Monitoring Interfaces and Openstack Support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. Figure:: monitoring_interfaces.png

   Monitoring Interfaces and Openstack Support

The figure above shows the DPDK L2 forwarding application running on a compute
node, sending and receiving traffic. collectd is also running on this compute
node retrieving the stats periodically from DPDK through the dpdkstat plugin
and publishing the retrieved stats to Ceilometer through the ceilometer plugin.

To see this demo in action please checkout: `Barometer OPNFV Summit demo`_

References
^^^^^^^^^^^
.. [1] https://collectd.org/wiki/index.php/Naming_schema
.. [2] https://github.com/collectd/collectd/blob/master/src/daemon/plugin.h
.. [3] https://collectd.org/wiki/index.php/Value_list_t
.. [4] https://collectd.org/wiki/index.php/Data_set
.. [5] https://collectd.org/documentation/manpages/types.db.5.shtml
.. [6] https://collectd.org/wiki/index.php/Data_source
.. [7] https://collectd.org/wiki/index.php/Meta_Data_Interface

.. _Barometer OPNFV Summit demo: https://prezi.com/kjv6o8ixs6se/software-fastpath-service-quality-metrics-demo/
.. _ceilometer plugin: https://github.com/openstack/collectd-ceilometer-plugin/tree/stable/mitaka

