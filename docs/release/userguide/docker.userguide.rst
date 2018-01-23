.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV Barometer Docker User Guide
===================================

.. contents::
   :depth: 3
   :local:

The intention of this user guide is to outline how to install and test the
Barometer projects Collectd, Influxdb and Grafana docker images which can be built from the Dockerfiles
available within the barometer repository.


Barometer docker images description
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

InfluxDB + Grafana Images
^^^^^^^^^^^^^^^^^^^^^^^^^

The Barometer project's InfluxDB and Grafana docker images are 2 docker images that database and graph
statistics reported by the Barometer collectd docker. InfluxDB is an open-source time series database
tool which stores the data from collectd for future analysis via Grafana, which is a open-source
metrics anlytics and visualisation suite which can be accessed through any browser.

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

Build the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Download the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want to use a pre-built barometer image, you can pull the barometer
image from https://hub.docker.com/r/opnfv/barometer-collectd/

.. code:: bash

    $ docker pull opnfv/barometer-collectd


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

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti opnfv/barometer-collectd /bin/bash

Check your docker image is running

.. code:: bash

   sudo docker ps

Build the influxdb + Grafana docker images
------------------------------------------

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

Download the InfluxDB and Grafana docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you wish to use pre-built barometer project's influxdb and grafana images, you can pull the
images from https://hub.docker.com/r/opnfv/barometer-influxdb/ and https://hub.docker.com/r/opnfv/barometer-grafana/

.. note::
     If your preference is to build images locally please see sections `Build the InfluxDB Image`_ and
     `Build the Grafana Image`_

.. code:: bash

    $ docker pull opnfv/barometer-influxdb
    $ docker pull opnfv/barometer-grafana

.. note::
     If you have pulled the pre-built barometer-influxdb and barometer-grafana images there is no
     requirement to complete steps outlined in  sections `Build the InfluxDB Image`_ and
     `Build the Grafana Image`_ and you can proceed directly to section
     `Run the Influxdb and Grafana Images`_ If you wish to run the barometer-influxdb and
     barometer-grafana images via Docker Compose proceed directly to section
     `Docker Compose: Run InfluxDB and Grafana Images`_.

Build the InfluxDB Image
^^^^^^^^^^^^^^^^^^^^^^^^^

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

Build the Grafana Image
^^^^^^^^^^^^^^^^^^^^^^^

Build Grafana image from Dockerfile

.. code:: bash

  $ cd barometer/docker/barometer-grafana
  $ sudo docker build -t opnfv/barometer-grafana --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f Dockerfile .

.. note::
         In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs to be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain an influxdb image:

.. code::

   REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
   opnfv/barometer-grafana      latest              05f2a3edd96b        3 hours ago         1.2GB

Run the Influxdb and Grafana Images
-----------------------------------

Run the InfluxDB  docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

   $ sudo docker run -tid --net=host -v /var/lib/influxdb:/var/lib/influxdb -p 8086:8086 -p 25826:25826  opnfv/barometer-influxdb

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti opnfv/barometer-influxdb /bin/bash

Check your docker image is running

.. code:: bash

   sudo docker ps

Run the Grafana docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting to an influxdb instance running on local system and adding own custom dashboards

.. code:: bash

   $ sudo docker run -tid --net=host -v /var/lib/grafana:/var/lib/grafana -v ${PWD}/dashboards:/opt/grafana/dashboards -p 3000:3000 opnfv/barometer-grafana

Connecting to an influxdb instance running on remote system with hostname of someserver and IP address of 192.168.121.111

.. code:: bash

   $ sudo docker run -tid --net=host -v /var/lib/grafana:/var/lib/grafana -p 3000:3000 -e influxdb_host=someserver --add-host someserver:192.168.121.111 opnfv/barometer-grafana

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti opnfv/barometer-grafana /bin/bash

Check your docker image is running

.. code:: bash

   sudo docker ps

Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin

Docker Compose: Run InfluxDB and Grafana Images
-----------------------------------------------

Install docker-compose
^^^^^^^^^^^^^^^^^^^^^^

On the node where you want to run influxdb + grafana or the node where you want to run the VES app
container:

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

Run the InfluxDB and Grafana Images using docker compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

