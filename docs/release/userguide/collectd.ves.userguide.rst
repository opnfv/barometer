.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

==========================
VES Application User Guide
==========================
The Barometer repository contains a python based application for VES.

The application currently supports pushing platform relevant metrics through the
additional measurements field for VES.

Collectd has a ``write_kafka`` plugin that sends collectd metrics and values to
a Kafka Broker. The VES application uses Kafka Consumer to receive metrics
from the Kafka Broker.


Install Kafka Broker
--------------------

1. Dependencies: install JAVA & Zookeeper.

    JAVA:

    .. code:: bash

        $ sudo apt install default-jre

    CentOS 7.x use:

    .. code:: bash

        $ sudo yum install java-1.6.0-openjdk

    Zookeeper:

    .. code:: bash

        $ sudo apt install zookeeperd

    CentOS 7.x use:

    .. code:: bash

        $ sudo yum install zookeeper

    .. note:: You may need to add the repository that contains zookeeper.
      To do so, follow the step below and try to install `zookeeper` again
      using steps above. Otherwise, skip next step.

    .. code:: bash

        $ sudo yum install
        https://archive.cloudera.com/cdh5/one-click-install/redhat/7/x86_64/cloudera-cdh-5-0.x86_64.rpm

    CentOS 7.x start zookeeper:

    .. code:: bash

        $ sudo zookeeper-server start

    if you get the error message like ``ZooKeeper data directory is missing at /var/lib/zookeeper``,
    during the start of zookeeper, it means that ZooKeeper is running on a
    given host at the first time. To fix that, initialize ZooKeeper data
    directory using the command below:

    .. code:: bash

        $ sudo /usr/lib/zookeeper/bin/zkServer-initialize.sh
        No myid provided, be sure to specify it in /var/lib/zookeeper/myid if using non-standalone

    To test if Zookeeper is running as a daemon.

    .. code:: bash

        $ telnet localhost 2181

    Type 'ruok' & hit enter.
    Expected response is 'imok'. Zookeeper is running fine.

    .. note::

        VES doesn't work with version 0.9.4 of kafka-python.
        The recommended/tested version is 1.3.3.

    .. code:: bash

        $ sudo yum install python-pip
        $ sudo pip install kafka-python

2. Download Kafka:

    .. code:: bash

        $ wget "http://www-eu.apache.org/dist/kafka/0.11.0.0/kafka_2.11-0.11.0.0.tgz"

3. Extract the archive:

    .. code:: bash

        $ tar -xvzf kafka_2.11-0.11.0.0.tgz

4. Configure Kafka Server:

    .. code:: bash

        $ vi kafka_2.11-0.11.0.0/config/server.properties

    By default Kafka does not allow you to delete topics. Please uncomment:

    .. code:: bash

        delete.topic.enable=true

5. Start the Kafka Server.

    Run 'kafka-server-start.sh' with nohup as a background process:

    .. code:: bash

        $ sudo nohup kafka_2.11-0.11.0.0/bin/kafka-server-start.sh \
          kafka_2.11-0.11.0.0/config/server.properties > kafka_2.11-0.11.0.0/kafka.log 2>&1 &

6. Test Kafka Broker Installation

    To test if the installation worked correctly there are two scripts, producer and consumer scripts.
    These will allow you to see messages pushed to broker and receive from broker.

    Producer (Publish "Hello World"):

    .. code:: bash

        $ echo "Hello, World" | kafka_2.11-0.11.0.0/bin/kafka-console-producer.sh \
          --broker-list localhost:9092 --topic TopicTest > /dev/null

    Consumer (Receive "Hello World"):

    .. code:: bash

        $ kafka_2.11-0.11.0.0/bin/kafka-console-consumer.sh --zookeeper \
          localhost:2181 --topic TopicTest --from-beginning


Install collectd
----------------

Install development tools:

.. code:: bash

    $ sudo yum group install 'Development Tools'

.. The libkafka installed via yum pkg manager is 0.11.0 which doesn't work with
   collectd (compilation issue). Thus, we have to use the library installed
   from sources using latest stable version which works with collectd.

Install Apache Kafka C/C++ client library:

.. code:: bash

    $ git clone https://github.com/edenhill/librdkafka.git ~/librdkafka
    $ cd ~/librdkafka
    $ git checkout -b v0.9.5 v0.9.5
    $ ./configure --prefix=/usr
    $ make
    $ sudo make install

Build collectd with Kafka support:

.. code:: bash

    $ git clone https://github.com/collectd/collectd.git ~/collectd
    $ cd ~/collectd
    $ ./build.sh
    $ ./configure --with-librdkafka=/usr --without-perl-bindings --enable-perl=no
    $ make && sudo make install

Configure and start collectd. Create ``/opt/collectd/etc/collectd.conf``
collectd configuration file as following:

.. note:: The following collectd configuration file allows user to run VES
   application in the guest mode. To run the VES in host mode, please follow
   the `Configure VES in host mode`_ steps.

.. include:: collectd-ves-guest.conf
   :code: bash

Start collectd process as a service as described in :ref:`install-collectd-as-a-service`.

..  Start collectd process as a service as described in `Barometer User Guide
    <http://artifacts.opnfv.org/barometer/docs/index.html#installing-collectd-as-a-service>`_.


Setup VES Test Collector
------------------------

.. note:: Test Collector setup is required only for VES application testing
   purposes.

Install dependencies:

.. code:: bash

    $ sudo pip install jsonschema

Clone VES Test Collector:

.. code:: bash

    $ git clone https://github.com/att/evel-test-collector.git ~/evel-test-collector

Modify VES Test Collector config file to point to existing log directory and
schema file:

.. code:: bash

    $ sed -i.back 's/^\(log_file[ ]*=[ ]*\).*/\1collector.log/' ~/evel-test-collector/config/collector.conf
    $ sed -i.back 's/^\(schema_file[ ]*=.*\)event_format_updated.json$/\1CommonEventFormat.json/' ~/evel-test-collector/config/collector.conf

Start VES Test Collector:

.. code:: bash

    $ cd ~/evel-test-collector/code/collector
    $ nohup python ./collector.py --config ../../config/collector.conf > collector.stdout.log &


Setup VES application (guest mode)
----------------------------------

Install dependencies:

.. code:: bash

    $ sudo pip install pyyaml

Clone Barometer repo:

.. code:: bash

    $ git clone https://gerrit.opnfv.org/gerrit/barometer ~/barometer
    $ cd ~/barometer/3rd_party/collectd-ves-app/ves_app
    $ nohup python ves_app.py --events-schema=guest.yaml --config=ves_app_config.conf > ves_app.stdout.log &

.. note::

    The above configuration is used for a localhost. The VES application can be
    configured to use remote real VES collector and remote Kafka server. To do
    so, the IP addresses/host names needs to be changed in ``collector.conf``
    and ``ves_app_config.conf`` files accordingly.


Configure VES in host mode
--------------------------

Running the VES in host mode looks like steps described in
`Setup VES application (guest mode)`_ but with the following exceptions:

- The ``host.yaml`` configuration file should be used instead of ``guest.yaml``
  file when VES application is running.

- Collectd should be running on host machine only.

- Addition ``libvirtd`` dependencies needs to be installed on a host where
  collectd daemon is running. To install those dependencies, see :ref:`virt-plugin`
  section of Barometer user guide.

- At least one VM instance should be up and running by hypervisor on the host.

- The next (minimum) configuration needs to be provided to collectd to be able
  to generate the VES message to VES collector.

  .. include:: collectd-ves-host.conf
     :code: bash

  to apply this configuration, the ``/opt/collectd/etc/collectd.conf`` file
  needs to be modified based on example above and collectd daemon needs to
  be restarted using the command below:

  .. code:: bash

    $ sudo systemctl restart collectd

.. note:: The list of the plugins can be extented depends on your needs.


VES application configuration description
-----------------------------------------

**Details of the Vendor Event Listener REST service**

REST resources are defined with respect to a ``ServerRoot``::

    ServerRoot = https://{Domain}:{Port}/{optionalRoutingPath}

REST resources are of the form::

    {ServerRoot}/eventListener/v{apiVersion}`
    {ServerRoot}/eventListener/v{apiVersion}/{topicName}`
    {ServerRoot}/eventListener/v{apiVersion}/eventBatch`

Within the VES directory (``3rd_party/collectd-ves-app/ves_app``) there is a
configuration file called ``ves_app.conf``. The description of the
configuration options are described below:

**Domain** *"host"*
  VES domain name. It can be IP address or hostname of VES collector
  (default: ``127.0.0.1``)

**Port** *port*
  VES port (default: ``30000``)

**Path** *"path"*
  Used as the "optionalRoutingPath" element in the REST path (default: empty)

**Topic** *"path"*
  Used as the "topicName" element in the REST  path (default: empty)

**UseHttps** *true|false*
  Allow application to use HTTPS instead of HTTP (default: ``false``)

**Username** *"username"*
  VES collector user name (default: empty)

**Password** *"passwd"*
  VES collector password (default: empty)

**SendEventInterval** *interval*
  This configuration option controls how often (sec) collectd data is sent to
  Vendor Event Listener (default: ``20``)

**ApiVersion** *version*
  Used as the "apiVersion" element in the REST path (default: ``5.1``)

**KafkaPort** *port*
  Kafka Port (Default ``9092``)

**KafkaBroker** *host*
  Kafka Broker domain name. It can be an IP address or hostname of local or remote server
  (default: ``localhost``)


VES notification support
------------------------

The VES application already supports YAML notification definitions but due to
the collectd Kafka plugin limitations, collectd notifications cannot be received
by the VES application. Thus, the VES notification (defined by YAML) will not be
generated and sent to VES collector.
