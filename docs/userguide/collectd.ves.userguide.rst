.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

collectd VES plugin
===================
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

where "/path/to/your/python/modules" is the path to where you cloned this repo

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

**GuestRunning** *true|false*
  This option is used if the collectd is running on a guest machine, e.g this
  option should be set to `true` in this case. Defaults to `false`.

**SendEventInterval** *interval*
  This configuration option controls how often (sec) collectd data is sent to
  Vendor Event Listener (default: `20`)

**ApiVersion** *version*
  Used as the "apiVersion" element in the REST path (default: `1`)

Other collectd.conf configurations
----------------------------------
Please ensure that FQDNLookup is set to false

.. code:: bash

    FQDNLookup   false

Please ensure that the virt plugin is enabled and configured as follows. This configuration
is is required only on a host side ('GuestRunning' = false).

.. code:: bash

    LoadPlugin virt

    <Plugin virt>
            Connection "qemu:///system"
            RefreshInterval 60
            HostnameFormat uuid
    </Plugin>

Please ensure that the cpu plugin is enabled and configured as follows

.. code:: bash

    LoadPlugin cpu

    <Plugin cpu>
        ReportByCpu false
        ValuesPercentage true
    </Plugin>

**Note**: The `ReportByCpu` option should be set to `true` (default) if VES pugin
is running on guest machine ('GuestRunning' = true).

Please ensure that the aggregation plugin is enabled and configured as follows
(required if 'GuestRunning' = true)

.. code:: bash

    LoadPlugin aggregation

    <Plugin aggregation>
        <Aggregation>
                Plugin "cpu"
                Type "percent"
                GroupBy "Host"
                GroupBy "TypeInstance"
                SetPlugin "cpu-aggregation"
                CalculateAverage true
        </Aggregation>
    </Plugin>

If plugin is running on a guest side, it is important to enable uuid plugin
too. In this case the hostname in event message will be represented as UUID
instead of system host name.

.. code:: bash

  LoadPlugin uuid

If custom UUID needs to be provided, the following configuration is required in collectd.conf
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

A good example of collectD notification is monitoring of CPU load on a host or guest using
'threshold' plugin. The following configuration will setup VES plugin to send 'Fault'
event every time a CPU idle value is out of range (e.g.: WARNING: CPU-IDLE < 50%, CRITICAL:
CPU-IDLE < 30%) and send 'Fault' NORMAL event if CPU idle value is back to normal.

.. code:: bash

    LoadPlugin threshold

    <Plugin "threshold">
         <Plugin "cpu-aggregation">
            <Type "percent">
              WarningMin    50.0
              WarningMax   100.0
              FailureMin    30.0
              FailureMax   100.0
              Instance "idle"
              Hits 1
            </Type>
        </Plugin>
    </Plugin>

More detailed information on how to configure collectD thresholds(memory, cpu
etc.) can be found here at
https://collectd.org/documentation/manpages/collectd-threshold.5.shtml
