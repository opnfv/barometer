.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

==========================
VES Application User Guide
==========================
The Barometer repository contains a python based application for VES.

The application currently supports pushing platform relevant metrics through the
additional measurements field for VES.

Collectd has a write_kafka plugin that will send collectd metrics and values to
a Kafka Broker.
The VES application uses Kafka Consumer to receive metrics from the Kafka
Broker.

Installation Instructions:
--------------------------
1. Clone this repo:

    .. code:: bash

        git clone https://gerrit.opnfv.org/gerrit/barometer

2. Install collectd

    .. code:: bash

       $ sudo apt-get install collectd

3. Modify the collectd configuration script: `/etc/collectd/collectd.conf`

    .. code:: bash

        <Plugin write_kafka>
            Property "metadata.broker.list" "localhost:9092"
            <Topic "collectd">
                Format JSON
            </Topic>
        </Plugin>

VES application configuration description:
------------------------------------------

Within the VES directory there is a configuration file called 'ves_app.conf'.

.. note:: Details of the Vendor Event Listener REST service

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
  Allow application to use HTTPS instead of HTTP (default: `false`)

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

**KafkaPort** *port*
  Kafka Port (Default ``9092``)

**KafkaBroker** *host*
  Kafka Broker domain name. It can be an IP address or hostname (default: localhost)

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

.. note::

    The ``ReportByCpu`` option should be set to `true` (default)
    if VES pugin is running on guest machine ('GuestRunning' = true).

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

If application is running on a guest side, it is important to enable uuid plugin
too. In this case the hostname in event message will be represented as UUID
instead of system host name.

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

VES application with collectd notifications example
---------------------------------------------------

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

Install Kafka Broker
--------------------

1. Dependencies: install JAVA & Zookeeper.

    JAVA:

    .. code:: bash

        $ sudo apt install default-jre

    Zookeeper:

    .. code:: bash

        $ sudo apt install zookeeperd

    To test if Zookeeper is running as a daemon.

    .. code:: bash

        $ sudo telnet localhost 2181

    Type 'ruok' & hit enter.
    Expected response is 'imok'. Zookeeper is running fine.

    .. note::

        VES doesn't work with version 0.9.4 of kafka-python.
        The recommended/tested version is 1.3.3.

    .. code:: bash

        $ sudo pip install kafka-python

2. Download Kafka:

    .. code:: bash

        $ sudo wget "http://www-eu.apache.org/dist/kafka/0.11.0.0/kafka_2.11-0.11.0.0.tgz"

3. Extract the archive:

    .. code:: bash

        $ sudo tar -xvzf kafka_2.11-0.11.0.0.tgz

4. Configure Kafka Server:

    .. code:: bash

        $ sudo vi kafka_2.11-0.11.0.0/config/server.properties

    By default Kafka does not allow you to delete topics. Please uncomment:

    .. code:: bash

        delete.topic.enable=true

5. Start the Kafka Server.

    Run 'kafka-server-start.sh' with nohup as a background process:

    .. code:: bash

        $ sudo nohup kafka_2.11-0.11.0.0/bin/kafka-server-start.sh \
          kafka_2.11-0.11.0.0/config/server.properties > kafka_2.11-0.11.0.0/kafka.log 2>&1 &

6. Test Kafka Broker Installation

    To test if the installation worked correctly there is two scripts, producer and consumer scripts.
    These will allow you to see messages pushed to broker and receive from broker.

    Producer (Publish "Hello World"):

    .. code:: bash

        $ echo "Hello, World" | kafka_2.11-0.11.0.0/bin/kafka-console-producer.sh \
          --broker-list localhost:9092 --topic TopicTest > /dev/null

    Consumer (Receive "Hello World"):

    .. code:: bash

        $ kafka_2.11-0.11.0.0/bin/kafka-console-consumer.sh --zookeeper \
          localhost:2181 --topic TopicTest --from-beginning
