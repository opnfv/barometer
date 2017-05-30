.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

==============================
collectd VES plugin User Guide
==============================
The Barometer repository contains a python based write plugin for VES.

The plugin currently supports pushing platform relevant metrics through the
additional measurements field for VES.

**Please note**: Hardcoded configuration values will be modified so that they
are configurable through the configuration file.

Installation Instructions:
--------------------------
1. Clone this repo
2. Install collectd

.. code:: bash

   $ sudo apt-get install collectd

3. Modify the collectd configuration script: `/etc/collectd/collectd.conf`

.. code:: bash

    <LoadPlugin python>
      Globals true
    </LoadPlugin>

    <Plugin python>
      ModulePath "/path/to/your/python/modules"
      LogTraces true
      Interactive false
      Import "ves_plugin"
    <Module ves_plugin>
    # VES plugin configuration (see next section below)
    </Module>
    </Plugin>

where "/path/to/your/python/modules" is the path to ves_plugin.py,
which is located in this repo.

VES python plugin configuration description:
--------------------------------------------

**Note** Details of the Vendor Event Listener REST service

REST resources are defined with respect to a ServerRoot:

.. code:: bash

    ServerRoot = https://{Domain}:{Port}/{optionalRoutingPath}

REST resources are of the form:

.. code:: bash

    {ServerRoot}/eventListener/v{apiVersion}`
    {ServerRoot}/eventListener/v{apiVersion}/{topicName}`
    {ServerRoot}/eventListener/v{apiVersion}/eventBatch`

**Domain** *"host"*
  VES domain name. It can be IP address or hostname of VES collector
  (default: `127.0.0.1`)

**Port** *port*
  VES port (default: `30000`)

**Path** *"path"*
  Used as the "optionalRoutingPath" element in the REST path (default: `empty`)

**Topic** *"path"*
  Used as the "topicName" element in the REST  path (default: `empty`)

**UseHttps** *true|false*
  Allow plugin to use HTTPS instead of HTTP (default: `false`)

**Username** *"username"*
  VES collector user name (default: `empty`)

**Password** *"passwd"*
  VES collector password (default: `empty`)

**FunctionalRole** *"role"*
  Used as the 'functionalRole' field of 'commonEventHeader' event (default:
  `Collectd VES Agent`)

**SendEventInterval** *interval*
  This configuration option controls how often (sec) collectd data is sent to
  Vendor Event Listener (default: `20`)

**ApiVersion** *version*
  Used as the "apiVersion" element in the REST path (default: `5.1`)

Other collectd.conf configurations
----------------------------------
Please ensure that FQDNLookup is set to false

.. code:: bash

    FQDNLookup   false

Please ensure that the virt plugin is enabled and configured as follows.

.. code:: bash

    LoadPlugin virt

    <Plugin virt>
            Connection "qemu:///system"
            RefreshInterval 60
            HostnameFormat uuid
            PluginInstanceFormat name
            ExtraStats "cpu_util perf"
    </Plugin>


.. note:: For more detailed information on the `virt` plugin configuration,
  requirements etc., please see the userguide of the collectd virt plugin.

Please ensure that the cpu plugin is enabled and configured as follows

.. code:: bash

    LoadPlugin cpu

    <Plugin cpu>
        ReportByCpu false
        ValuesPercentage true
    </Plugin>

To report the host name as a UUID the uuid plugin can be used.

.. code:: bash

    LoadPlugin uuid

If a custom UUID needs to be provided, the following configuration is required in collectd.conf
file:

.. code:: bash

    <Plugin uuid>
        UUIDFile "/etc/uuid"
    </Plugin>

Where "/etc/uuid" is a file containing custom UUID.

Please also ensure that the following plugins are enabled:

.. code:: bash

    LoadPlugin disk
    LoadPlugin interface
    LoadPlugin memory

VES plugin notification example
-------------------------------

A good example of collectD notification is monitoring of the total CPU usage on a VM
using the 'threshold' plugin. The following configuration will setup VES plugin to send 'Fault'
event every time a total VM CPU value is out of range (e.g.: WARNING: VM CPU TOTAL > 50%,
CRITICAL: VM CPU TOTAL > 96%) and send 'Fault' NORMAL event if the CPU value is back
to normal. In the example below, there is one VM with two CPUs configured which is running
on the host with a total of 48 cores. Thus, the threshold value 2.08 (100/48) means that
one CPU of the VM is fully loaded (e.g.: 50% of total CPU usage of the VM) and 4.0 means
96% of total CPU usage of the VM. Those values can also be obtained by virt-top
command line tool.

.. code:: bash

    LoadPlugin threshold

    <Plugin "threshold">
        <Plugin "virt">
            <Type "percent">
                WarningMax    2.08
                FailureMax    4.0
                Instance      "virt_cpu_total"
            </Type>
        </Plugin>
    </Plugin>

More detailed information on how to configure collectD thresholds can be found at
https://collectd.org/documentation/manpages/collectd-threshold.5.shtml
