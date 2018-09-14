.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV Barometer Docker User Guide
===================================

.. contents::
   :depth: 3
   :local:

The intention of this user guide is to outline how to install and test the Barometer project's
docker images. The `OPNFV docker hub <https://hub.docker.com/u/opnfv/?page=1>`_ contains 5 docker
images from the Barometer project:

 1. `Collectd docker image <https://hub.docker.com/r/opnfv/barometer-collectd/>`_
 2. `Influxdb docker image <https://hub.docker.com/r/opnfv/barometer-influxdb/>`_
 3. `Grafana docker image <https://hub.docker.com/r/opnfv/barometer-grafana/>`_
 4. `Kafka docker image <https://hub.docker.com/r/opnfv/barometer-kafka/>`_
 5. `VES application docker image <https://hub.docker.com/r/opnfv/barometer-ves/>`_

For description of images please see section `Barometer Docker Images Description`_

For steps to build and run Collectd image please see section `Build and Run Collectd Docker Image`_

For steps to build and run InfluxDB and Grafana images please see section `Build and Run InfluxDB and Grafana Docker Images`_

For steps to build and run VES and Kafka images please see section `Build and Run VES and Kafka Docker Images`_

For overview of running VES application with Kafka please see the `VES Application User Guide
<http://docs.opnfv.org/en/latest/submodules/barometer/docs/release/userguide/collectd.ves.userguide.html>`_

Barometer Docker Images Description
-----------------------------------

.. Describe the specific features and how it is realised in the scenario in a brief manner
.. to ensure the user understand the context for the user guide instructions to follow.

Barometer Collectd Image
^^^^^^^^^^^^^^^^^^^^^^^^
The barometer collectd docker image gives you a collectd installation that includes all
the barometer plugins.

.. note::
   The Dockerfile is available in the docker/barometer-collectd directory in the barometer repo.
   The Dockerfile builds a CentOS 7 docker image.
   The container MUST be run as a privileged container.

Collectd is a daemon which collects system performance statistics periodically
and provides a variety of mechanisms to publish the collected metrics. It
supports more than 90 different input and output plugins. Input plugins
retrieve metrics and publish them to the collectd deamon, while output plugins
publish the data they receive to an end point. Collectd also has infrastructure
to support thresholding and notification.

Collectd docker image has enabled the following collectd plugins (in addition
to the standard collectd plugins):

* hugepages plugin
* Open vSwitch events Plugin
* Open vSwitch stats Plugin
* mcelog plugin
* PMU plugin
* RDT plugin
* virt
* SNMP Agent
* Kafka_write plugin

Plugins and third party applications in Barometer repository that will be available in the
docker image:

* Open vSwitch PMD stats
* ONAP VES application
* gnocchi plugin
* aodh plugin
* Legacy/IPMI

InfluxDB + Grafana Docker Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Barometer project's InfluxDB and Grafana docker images are 2 docker images that database and graph
statistics reported by the Barometer collectd docker. InfluxDB is an open-source time series database
tool which stores the data from collectd for future analysis via Grafana, which is a open-source
metrics anlytics and visualisation suite which can be accessed through any browser.

VES + Kafka Docker Images
^^^^^^^^^^^^^^^^^^^^^^^^^

The Barometer project's VES application and Kafka docker images are based on a CentOS 7 image. Kafka
docker image has a dependancy on `Zookeeper <https://zookeeper.apache.org/>`_. Kafka must be able to
connect and register with an instance of Zookeeper that is either running on local or remote host.
Kafka recieves and stores metrics recieved from Collectd. VES application pulls latest metrics from Kafka
which it normalizes into VES format for sending to a VES collector. Please see details in `VES Application User Guide
<http://docs.opnfv.org/en/latest/submodules/barometer/docs/release/userguide/collectd.ves.userguide.html>`_

Download and Run Docker Images with Ansible-Playbook
----------------------------------------------------

Install Ansible
^^^^^^^^^^^^^^^
.. note::
   * sudo permissions or root access are required to install ansible.
   * ansible version needs to be 2.4+, because usage of import/include statements

To install ansible on Ubuntu:

.. code:: bash

    $ sudo apt-get install python
    $ sudo apt-get install python-pip
    $ sudo pip install 'ansible==2.6.3'

To install ansible on CentOS 7:

.. code:: bash

    $ sudo yum install python
    $ sudo yum install epel-release
    $ sudo yum install python-pip
    $ sudo pip install 'ansible==2.6.3'

Clone barometer repo
^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ git clone https://gerrit.opnfv.org/gerrit/barometer
    $ cd barometer/docker/ansible

Create inventory file
^^^^^^^^^^^^^^^^^^^^^
Create file with hosts: ~/inventory.inv

.. code:: bash

    [collectd_hosts]
    localhost
    [influxdb_hosts]
    localhost
    [grafana_hosts]
    localhost
    [kafka_hosts]
    localhost
    [ves_hosts]
    localhost

Change localhost to different hosts where neccessary.
Hosts for influxdb and grafana are required only for collectd_service.yml.
Hosts for kafka and ves are required only for collectd_ves.yml.

To change host for infludb edit network_ip_addr in ./roles/config_files/vars/main.yml and influxdb_hostname, influxdb_host_ip in roles/run_grafana/vars/main.yml.
To change host for kafka edit kafka_ip_addr in ./roles/config_files/vars/main.yml.

Configure ssh keys
^^^^^^^^^^^^^^^^^^

Generate ssh keys if not present, otherwise move onto next step.

.. code:: bash

    $ ssh-keygen

Coppy ssh key to all target hosts. It requires to provide root password. The example is for localhost.

.. code:: bash

    $ ssh-copy-id root@localhost

Download collectd+influxdb+grafana containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ sudo ansible-playbook -i ~/inventory.inv collectd_service.yml

Check the three containers are running, the output of docker ps should be similar to:

.. code:: bash

    $ sudo docker ps
    CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS               NAMES
    a033aeea180d        opnfv/barometer-grafana    "/run.sh"                9 days ago          Up 7 minutes                            bar-grafana
    1bca2e4562ab        opnfv/barometer-influxdb   "/entrypoint.sh in..."   9 days ago          Up 7 minutes                            bar-influxdb
    daeeb68ad1d5        opnfv/barometer-collectd   "/run_collectd.sh ..."   9 days ago          Up 7 minutes                            bar-collectd

To make some changes when a container is running run:

.. code:: bash

    $ sudo docker exec -ti <CONTAINER ID> /bin/bash

Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin

The collectd configuration files can be accessed directly on target system in '/opt/collectd/etc/collectd.conf.d'.
It can be used for manual changes or enable/disable plugins. If configuration has been modified it is required to
restart collectd:

.. code:: bash

    $ sudo docker restart bar-collectd

Download collectd+kafka+ves containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before running Kafka an instance of zookeeper is required. See `Run Kafka docker image`_ for notes on how to run it.
The 'zookeeper_hostname' and 'broker_id' can be set in ./roles/run_kafka/vars/main.yml.

.. code:: bash

    $ sudo ansible-playbook -i ~/inventory.inv collectd_ves.yml

Check the three containers are running, the output of docker ps should be similar to:

.. code:: bash

    $ sudo docker ps
    CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS                     PORTS               NAMES
    8b095ad94ea1        zookeeper:3.4.11           "/docker-entrypoin..."   7 minutes ago       Up 7 minutes                                   awesome_jennings
    eb8bba3c0b76        opnfv/barometer-ves        "./start_ves_app.s..."   21 minutes ago      Up 6 minutes                                   bar-ves
    86702a96a68c        opnfv/barometer-kafka      "/src/start_kafka.sh"    21 minutes ago      Up 6 minutes                                   bar-kafka
    daeeb68ad1d5        opnfv/barometer-collectd   "/run_collectd.sh ..."   13 days ago         Up 6 minutes                                   bar-collectd


To make some changes when a container is running run:

.. code:: bash

    $ sudo docker exec -ti <CONTAINER ID> /bin/bash

List of default plugins for collectd container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the collectd is started with default configuration which includes the followin plugins:
   * csv, contextswitch, cpu, cpufreq, df, disk, ethstat, ipc, irq, load, memory, numa, processes, swap, turbostat, uuid, uptime, exec, hugepages, intel_pmu, ipmi, write_kafka, logfile, mcelog, network, intel_rdt, rrdtool, snmp_agent, syslog, virt, ovs_stats, ovs_events

Some of the plugins are loaded depending on specific system requirements and can be omitted if dependency is not met, this is the case for:
   * hugepages, ipmi, mcelog, intel_rdt, virt, ovs_stats, ovs_events

List and description of tags used in ansible scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tags can be used to run a specific part of the configuration without running the whole playbook.
To run a specific parts only:

.. code:: bash

    $ sudo ansible-playbook -i ~/inventory.inv collectd_service.yml --tags "syslog,cpu"

To disable some parts or plugins:

.. code:: bash

    $ sudo ansible-playbook -i ~/inventory.inv collectd_service.yml --skip-tags "syslog,cpu"

List of available tags:

install_docker
  Install docker and required dependencies with package manager.

add_docker_proxy
  Configure proxy file for docker service if proxy is set on host environment.

rm_config_dir
  Remove collectd config files.

copy_additional_configs
  Copy additional configuration files to target system. Path to additional configuration is stored in ./roles/config_files/vars/main.yml as additional_configs_path.

plugins tags
  The following tags can be used to enable/disable plugins: csv, contextswitch, cpu, cpufreq, df, disk, ethstat, ipc, irq, load, memory, numa, processes, swap, turbostat, uptime, exec, hugepages, ipmi, kafka, logfile, mcelogs, network, pmu, rdt, rrdtool, snmp, syslog, virt, ovs_stats, ovs_events.

Installing Docker
-----------------
.. Describe the specific capabilities and usage for <XYZ> feature.
.. Provide enough information that a user will be able to operate the feature on a deployed scenario.

On Ubuntu
^^^^^^^^^^
.. note::
   * sudo permissions are required to install docker.
   * These instructions are for Ubuntu 16.10

To install docker:

.. code:: bash

    $ sudo apt-get install curl
    $ sudo curl -fsSL https://get.docker.com/ | sh
    $ sudo usermod -aG docker <username>
    $ sudo systemctl status docker

Replace <username> above with an appropriate user name.

On CentOS
^^^^^^^^^^
.. note::
   * sudo permissions are required to install docker.
   * These instructions are for CentOS 7

To install docker:

.. code:: bash

    $ sudo yum remove docker docker-common docker-selinux docker-engine
    $ sudo yum install -y yum-utils  device-mapper-persistent-data  lvm2
    $ sudo yum-config-manager   --add-repo    https://download.docker.com/linux/centos/docker-ce.repo
    $ sudo yum-config-manager --enable docker-ce-edge
    $ sudo yum-config-manager --enable docker-ce-test
    $ sudo yum install docker-ce
    $ sudo usermod -aG docker <username>
    $ sudo systemctl status docker

Replace <username> above with an appropriate user name.

.. note::
   If this is the first time you are installing a package from a recently added
   repository, you will be prompted to accept the GPG key, and the key’s
   fingerprint will be shown. Verify that the fingerprint is correct, and if so,
   accept the key. The fingerprint should match060A 61C5 1B55 8A7F 742B 77AA C52F
   EB6B 621E 9F35.

        Retrieving key from https://download.docker.com/linux/centos/gpg
        Importing GPG key 0x621E9F35:
         Userid     : "Docker Release (CE rpm) <docker@docker.com>"
         Fingerprint: 060a 61c5 1b55 8a7f 742b 77aa c52f eb6b 621e 9f35
         From       : https://download.docker.com/linux/centos/gpg
        Is this ok [y/N]: y

Proxy Configuration:
^^^^^^^^^^^^^^^^^^^^
.. note::
   This applies for both CentOS and Ubuntu.

If you are behind an HTTP or HTTPS proxy server, you will need to add this
configuration in the Docker systemd service file.

1. Create a systemd drop-in directory for the docker service:

.. code:: bash

   $ sudo mkdir -p /etc/systemd/system/docker.service.d

2. Create a file
called /etc/systemd/system/docker.service.d/http-proxy.conf that adds
the HTTP_PROXY environment variable:

.. code:: bash

   [Service]
   Environment="HTTP_PROXY=http://proxy.example.com:80/"

Or, if you are behind an HTTPS proxy server, create a file
called /etc/systemd/system/docker.service.d/https-proxy.conf that adds
the HTTPS_PROXY environment variable:

.. code:: bash

    [Service]
    Environment="HTTPS_PROXY=https://proxy.example.com:443/"

Or create a single file with all the proxy configurations:
/etc/systemd/system/docker.service.d/proxy.conf

.. code:: bash

    [Service]
    Environment="HTTP_PROXY=http://proxy.example.com:80/"
    Environment="HTTPS_PROXY=https://proxy.example.com:443/"
    Environment="FTP_PROXY=ftp://proxy.example.com:443/"
    Environment="NO_PROXY=localhost"

3. Flush changes:

.. code:: bash

    $ sudo systemctl daemon-reload

4. Restart Docker:

.. code:: bash

    $ sudo systemctl restart docker

5. Check docker environment variables:

.. code:: bash

    sudo systemctl show --property=Environment docker

Test docker installation
^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
   This applies for both CentOS and Ubuntu.

.. code:: bash

   $ sudo docker run hello-world

The output should be something like:

.. code:: bash

   Unable to find image 'hello-world:latest' locally
   latest: Pulling from library/hello-world
   5b0f327be733: Pull complete
   Digest: sha256:07d5f7800dfe37b8c2196c7b1c524c33808ce2e0f74e7aa00e603295ca9a0972
   Status: Downloaded newer image for hello-world:latest

   Hello from Docker!
   This message shows that your installation appears to be working correctly.

   To generate this message, Docker took the following steps:
    1. The Docker client contacted the Docker daemon.
    2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    3. The Docker daemon created a new container from that image which runs the
       executable that produces the output you are currently reading.
    4. The Docker daemon streamed that output to the Docker client, which sent it
       to your terminal.

To try something more ambitious, you can run an Ubuntu container with:

.. code:: bash

    $ docker run -it ubuntu bash

Build and Run Collectd Docker Image
-----------------------------------

Download the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you wish to use a pre-built barometer image, you can pull the barometer
image from https://hub.docker.com/r/opnfv/barometer-collectd/

.. code:: bash

    $ docker pull opnfv/barometer-collectd

Build the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ git clone https://gerrit.opnfv.org/gerrit/barometer
    $ cd barometer/docker/barometer-collectd
    $ sudo docker build -t opnfv/barometer-collectd --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs to be
   passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain a barometer-collectd image:

.. code::

   REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-collectd     latest              05f2a3edd96b        3 hours ago         1.2GB
   centos                       7                   196e0ce0c9fb        4 weeks ago         197MB
   centos                       latest              196e0ce0c9fb        4 weeks ago         197MB
   hello-world                  latest              05a3bd381fc2        4 weeks ago         1.84kB

Run the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

   $ sudo docker run -tid --net=host -v `pwd`/../src/collectd_sample_configs:/opt/collectd/etc/collectd.conf.d \
    -v /var/run:/var/run -v /tmp:/tmp --privileged opnfv/barometer-collectd /run_collectd.sh

.. note::
   The docker collectd image contains configuration for all the collectd plugins. In the command
   above we are overriding /opt/collectd/etc/collectd.conf.d by mounting a host directory
   `pwd`/../src/collectd_sample_configs that contains only the sample configurations we are interested
   in running. *It's important to do this if you don't have DPDK, or RDT installed on the host*.
   Sample configurations can be found at:
   https://github.com/opnfv/barometer/tree/master/src/collectd/collectd_sample_configs

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

Build and Run InfluxDB and Grafana docker images
------------------------------------------------

Overview
^^^^^^^^
The barometer-influxdb image is based on the influxdb:1.3.7 image from the influxdb dockerhub. To
view detils on the base image please visit
`https://hub.docker.com/_/influxdb/  <https://hub.docker.com/_/influxdb/>`_ Page includes details of
exposed ports and configurable enviromental variables of the base image.

The barometer-grafana image is based on grafana:4.6.3 image from the grafana dockerhub. To view
details on the base image please visit
`https://hub.docker.com/r/grafana/grafana/ <https://hub.docker.com/r/grafana/grafana/>`_ Page
includes details on exposed ports and configurable enviromental variables of the base image.

The barometer-grafana image includes pre-configured source and dashboards to display statistics exposed
by the barometer-collectd image. The default datasource is an influxdb database running on localhost
but the address of the influxdb server can be modified when launching the image by setting the
environmental variables influxdb_host to IP or hostname of host on which influxdb server is running.

Additional dashboards can be added to barometer-grafana by mapping a volume to /opt/grafana/dashboards.
Incase where a folder is mounted to this volume only files included in this folder will be visible
inside barometer-grafana. To ensure all default files are also loaded please ensure they are included in
volume folder been mounted. Appropriate example are given in section `Run the Grafana docker image`_

Download the InfluxDB and Grafana docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you wish to use pre-built barometer project's influxdb and grafana images, you can pull the
images from https://hub.docker.com/r/opnfv/barometer-influxdb/ and https://hub.docker.com/r/opnfv/barometer-grafana/

.. note::
   If your preference is to build images locally please see sections `Build InfluxDB Docker Image`_ and
   `Build Grafana Docker Image`_

.. code:: bash

    $ docker pull opnfv/barometer-influxdb
    $ docker pull opnfv/barometer-grafana

.. note::
   If you have pulled the pre-built barometer-influxdb and barometer-grafana images there is no
   requirement to complete steps outlined in  sections `Build InfluxDB Docker Image`_ and
   `Build Grafana Docker Image`_ and you can proceed directly to section
   `Run the Influxdb and Grafana Images`_ If you wish to run the barometer-influxdb and
   barometer-grafana images via Docker Compose proceed directly to section
   `Docker Compose`_.

Build InfluxDB docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build influxdb image from Dockerfile

.. code:: bash

  $ cd barometer/docker/barometer-influxdb
  $ sudo docker build -t opnfv/barometer-influxdb --build-arg http_proxy=`echo $http_proxy` \
    --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs to
   be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain an influxdb image:

.. code::

   REPOSITORY                   TAG                 IMAGE ID            CREATED            SIZE
   opnfv/barometer-influxdb     latest              1e4623a59fe5        3 days ago         191MB

Build Grafana docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^

Build Grafana image from Dockerfile

.. code:: bash

  $ cd barometer/docker/barometer-grafana
  $ sudo docker build -t opnfv/barometer-grafana --build-arg http_proxy=`echo $http_proxy` \
    --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs to
   be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain an influxdb image:

.. code::

   REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-grafana      latest              05f2a3edd96b        3 hours ago         1.2GB

Run the Influxdb and Grafana Images
-----------------------------------

Run the InfluxDB docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

   $ sudo docker run -tid -v /var/lib/influxdb:/var/lib/influxdb -p 8086:8086 -p 25826:25826  opnfv/barometer-influxdb

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

Run the Grafana docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting to an influxdb instance running on local system and adding own custom dashboards

.. code:: bash

   $ sudo docker run -tid -v /var/lib/grafana:/var/lib/grafana -v ${PWD}/dashboards:/opt/grafana/dashboards \
     -p 3000:3000 opnfv/barometer-grafana

Connecting to an influxdb instance running on remote system with hostname of someserver and IP address
of 192.168.121.111

.. code:: bash

   $ sudo docker run -tid -v /var/lib/grafana:/var/lib/grafana -p 3000:3000 -e \
     influxdb_host=someserver --add-host someserver:192.168.121.111 opnfv/barometer-grafana

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin


Build and Run VES and Kafka Docker Images
------------------------------------------

Download VES and Kafka docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you wish to use pre-built barometer project's VES and kafka images, you can pull the
images from https://hub.docker.com/r/opnfv/barometer-ves/ and  https://hub.docker.com/r/opnfv/barometer-kafka/

.. note::
   If your preference is to build images locally please see sections `Build the Kafka Image`_ and
   `Build VES Image`_

.. code:: bash

    $ docker pull opnfv/barometer-kafka
    $ docker pull opnfv/barometer-ves

.. note::
   If you have pulled the pre-built images there is no requirement to complete steps outlined
   in sections `Build Kafka Docker Image`_ and `Build VES Docker Image`_ and you can proceed directly to section
   `Run Kafka Docker Image`_ If you wish to run the docker images via Docker Compose proceed directly to section `Docker Compose`_.

Build Kafka docker image
^^^^^^^^^^^^^^^^^^^^^^^^

Build Kafka docker image:

.. code:: bash

    $ cd barometer/docker/barometer-kafka
    $ sudo docker build -t opnfv/barometer-kafka --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs
   to be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain a barometer image:

.. code::

   REPOSITORY                TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-kafka     latest              05f2a3edd96b        3 hours ago         1.2GB

Build VES docker image
^^^^^^^^^^^^^^^^^^^^^^

Build VES application docker image:

.. code:: bash

    $ cd barometer/docker/barometer-ves
    $ sudo docker build -t opnfv/barometer-ves --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs
   to be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain a barometer image:

.. code::

   REPOSITORY                TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-ves       latest              05f2a3edd96b        3 hours ago         1.2GB

Run Kafka docker image
^^^^^^^^^^^^^^^^^^^^^^

.. note::
   Before running Kafka an instance of Zookeeper must be running for the Kafka broker to register
   with. Zookeeper can be running locally or on a remote platform. Kafka's broker_id and address of
   its zookeeper instance can be configured by setting values for environmental variables 'broker_id'
   and 'zookeeper_node'. In instance where 'broker_id' and/or 'zookeeper_node' is not set the default
   setting of broker_id=0 and zookeeper_node=localhost is used. In intance where Zookeeper is running
   on same node as Kafka and there is a one to one relationship between Zookeeper and Kafka, default
   setting can be used. The docker argument `add-host` adds hostname and IP address to
   /etc/hosts file in container

Run zookeeper docker image:

.. code:: bash

   $ sudo docker run -tid --net=host -p 2181:2181 zookeeper:3.4.11

Run kafka docker image which connects with a zookeeper instance running on same node with a 1:1 relationship

.. code:: bash

   $ sudo docker run -tid --net=host -p 9092:9092 opnfv/barometer-kafka


Run kafka docker image which connects with a zookeeper instance running on a node with IP address of
192.168.121.111 using broker ID of 1

.. code:: bash

   $ sudo docker run -tid --net=host -p 9092:9092 --env broker_id=1 --env zookeeper_node=zookeeper --add-host \
     zookeeper:192.168.121.111 opnfv/barometer-kafka

Run VES Application docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
   VES application uses configuration file ves_app_config.conf from directory
   barometer/3rd_party/collectd-ves-app/ves_app/config/ and host.yaml file from
   barometer/3rd_party/collectd-ves-app/ves_app/yaml/ by default. If you wish to use a custom config
   file it should be mounted to mount point /opt/ves/config/ves_app_config.conf. To use an alternative yaml
   file from folder barometer/3rd_party/collectd-ves-app/ves_app/yaml the name of the yaml file to use
   should be passed as an additional command. If you wish to use a custom file the file should be
   mounted to mount point /opt/ves/yaml/ Please see examples below

Run VES docker image with default configuration

.. code:: bash

   $ sudo docker run -tid --net=host opnfv/barometer-ves

Run VES docker image with guest.yaml files from barometer/3rd_party/collectd-ves-app/ves_app/yaml/

.. code:: bash

   $ sudo docker run -tid --net=host opnfv/barometer-ves guest.yaml


Run VES docker image with using custom config and yaml files. In example below yaml/ folder cotains
file named custom.yaml

.. code:: bash

   $ sudo docker run -tid --net=host -v ${PWD}/custom.config:/opt/ves/config/ves_app_config.conf \
     -v ${PWD}/yaml/:/opt/ves/yaml/ opnfv/barometer-ves custom.yaml

Build and Run LocalAgent and Redis Docker Images
-----------------------------------------------------

Download LocalAgent docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you wish to use pre-built barometer project's LocalAgent images, you can pull the
images from https://hub.docker.com/r/opnfv/barometer-localagent/

.. note::
   If your preference is to build images locally please see sections `Build LocalAgent Docker Image`_

.. code:: bash

    $ docker pull opnfv/barometer-localagent

.. note::
   If you have pulled the pre-built images there is no requirement to complete steps outlined
   in sections `Build LocalAgent Docker Image`_ and you can proceed directly to section
   `Run LocalAgent Docker Image`_ If you wish to run the docker images via Docker Compose proceed directly to section `Docker Compose`_.

Build LocalAgent docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build LocalAgent docker image:

.. code:: bash

    $ cd barometer/docker/barometer-dma
    $ sudo docker build -t opnfv/barometer-dma --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs
   to be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain a barometer image:

.. code::

   REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-dma          latest              2f14fbdbd498        3 hours ago         941 MB

Run Redis docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
   Before running LocalAgent, Redis must be running.

Run Redis docker image:

.. code:: bash

   $ sudo docker run -tid -p 6379:6379 --name barometer-redis redis

Check your docker image is running

.. code:: bash

   sudo docker ps

Run LocalAgent docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

Run LocalAgent docker image with default configuration

.. code:: bash

   $ cd barometer/docker/barometer-dma
   $ sudo mkdir /etc/barometer-dma
   $ sudo cp ../../src/dma/examples/config.toml /etc/barometer-dma/
   $ sudo vi /etc/barometer-dma/config.toml
   (edit amqp_password and os_password:OpenStack admin password)

   $ sudo su -
   (When there is no key for SSH access authentication)
   # ssh-keygen
   (Press Enter until done)
   (Backup if necessary)
   # cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys_org
   # cat ~/.ssh/authorized_keys_org ~/.ssh/id_rsa.pub \
     > ~/.ssh/authorized_keys
   # exit

   $ sudo docker run -tid --net=host --name server \
     -v /etc/barometer-dma:/etc/barometer-dma \
     -v /root/.ssh/id_rsa:/root/.ssh/id_rsa \
     -v /etc/collectd/collectd.conf.d:/etc/collectd/collectd.conf.d \
     opnfv/barometer-dma /server

   $ sudo docker run -tid --net=host --name infofetch \
     -v /etc/barometer-dma:/etc/barometer-dma \
     -v /var/run/libvirt:/var/run/libvirt \
     opnfv/barometer-dma /infofetch

   (Execute when installing the threshold evaluation binary)
   $ sudo docker cp infofetch:/threshold ./
   $ sudo ln -s ${PWD}/threshold /usr/local/bin/

Docker Compose
--------------

Install docker-compose
^^^^^^^^^^^^^^^^^^^^^^

On the node where you want to run influxdb + grafana or the node where you want to run the VES app
zookeeper and Kafka containers together:

.. note::
   The default configuration for all these containers is to run on the localhost. If this is not
   the model you want to use then please make the appropriate configuration changes before launching
   the docker containers.

1. Start by installing docker compose

.. code:: bash

   $ sudo curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-`uname -s`-`uname -m` -o /usr/bin/docker-compose

.. note::
   Use the latest Compose release number in the download command. The above command is an example,
   and it may become out-of-date. To ensure you have the latest version, check the Compose repository
   release page on GitHub.

2. Apply executable permissions to the binary:

.. code:: bash

   $ sudo chmod +x /usr/bin/docker-compose

3. Test the installation.

.. code:: bash

  $ sudo docker-compose --version

Run the InfluxDB and Grafana containers using docker compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Launch containers:

.. code:: bash

   $ cd barometer/docker/compose/influxdb-grafana/
   $ sudo docker-compose up -d

Check your docker images are running

.. code:: bash

   $ sudo docker ps

Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin

Run the Kafka, zookeeper and VES containers using docker compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Launch containers:

.. code:: bash

   $ cd barometer/docker/compose/ves/
   $ sudo docker-compose up -d

Check your docker images are running

.. code:: bash

   $ sudo docker ps

Testing the docker image
^^^^^^^^^^^^^^^^^^^^^^^^
TODO

References
^^^^^^^^^^^
.. [1] https://docs.docker.com/engine/admin/systemd/#httphttps-proxy
.. [2] https://docs.docker.com/engine/installation/linux/docker-ce/centos/#install-using-the-repository
.. [3] https://docs.docker.com/engine/userguide/


