.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>
.. _barometer-docker-userguide:

====================================
OPNFV Barometer Docker Install Guide
====================================

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

For overview of running VES application with Kafka please see the :ref:`VES Application User Guide <barometer-ves-userguide>`

For an alternative installation method using ansible, please see the :ref:`Barometer One Click Install Guide <barometer-oneclick-userguide>`. 

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
which it normalizes into VES format for sending to a VES collector. Please see details in 
:ref:`VES Application User Guide <barometer-ves-userguide>`

Installing Docker
-----------------
.. Describe the specific capabilities and usage for <XYZ> feature.
.. Provide enough information that a user will be able to operate the feature on a deployed scenario.

.. note::
   The below sections provide steps for manual installation and configuration
   of docker images. They are not neccessary if docker images were installed with
   use of Ansible-Playbook.

On Ubuntu
^^^^^^^^^
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
.. ::
         Userid     : "Docker Release (CE rpm) <docker@docker.com>"
         Fingerprint: 060a 61c5 1b55 8a7f 742b 77aa c52f eb6b 621e 9f35
         From       : https://download.docker.com/linux/centos/gpg
        Is this ok [y/N]: y

Manual proxy configuration for docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

   Trying to pull docker.io/library/hello-world...Getting image source signatures
   Copying blob 0e03bdcc26d7 done
   Copying config bf756fb1ae done
   Writing manifest to image destination
   Storing signatures

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
    $ docker run -it ubuntu bash

   Share images, automate workflows, and more with a free Docker ID:
    https://hub.docker.com/

   For more examples and ideas, visit:
    https://docs.docker.com/get-started/

Build and Run Collectd Docker Image
-----------------------------------

Collectd-barometer flavors
^^^^^^^^^^^^^^^^^^^^^^^^^^

Before starting to build and run the Collectd container, understand the available
flavors of Collectd containers:
  * barometer-collectd - stable release, based on collectd 5.11
  * barometer-collectd-latest - release based on collectd 'main' branch
  * barometer-collectd-experimental - release based on collectd 'main'
    branch that also includes set of experimental (not yet merged into upstream)
    pull requests

.. note::
   Experimental container is not tested across various OS'es and the stability
   of the container can change. Usage of experimental flavor is at users risk.

Stable `barometer-collectd` container is intended for work in production
environment as it is based on latest collectd official release.
`barometer-collectd-latest` and `barometer-collectd-experimental` containers
can be used in order to try new collectd features.
All flavors are located in `barometer` git repository - respective Dockerfiles
are stored in subdirectories of `docker/` directory


.. code:: bash

    $ git clone https://gerrit.opnfv.org/gerrit/barometer
    $ ls barometer/docker|grep collectd
    barometer-collectd
    barometer-collectd-latest
    barometer-collectd-experimental

.. note::
   Main directory of barometer source code (directory that contains 'docker',
   'docs', 'src' and systems sub-directories) will be referred as
   ``<BAROMETER_REPO_DIR>``

Download the collectd docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you wish to use a pre-built barometer image, you can pull the barometer
image from https://hub.docker.com/r/opnfv/barometer-collectd/

.. code:: bash

    $ docker pull opnfv/barometer-collectd

Build stable collectd container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ cd <BAROMETER_REPO_DIR>/docker/barometer-collectd
    $ sudo docker build -t opnfv/barometer-collectd --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` --network=host -f Dockerfile .

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

.. note::
   If you do not plan to use collectd-latest and collectd-experimental barometer
   containers, then you can proceed directly to section `Run the collectd stable docker image`_


Build collectd-latest container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ cd <BAROMETER_REPO_DIR>
    $ sudo docker build -t opnfv/barometer-collectd-latest \
     --build-arg http_proxy=`echo $http_proxy` \
     --build-arg https_proxy=`echo $https_proxy` --network=host -f \
     docker/barometer-collectd-latest/Dockerfile .

.. note::
   For `barometer-collectd-latest` and `barometer-collectd-experimental` containers
   proxy parameters should be passed only if system is behind an HTTP or HTTPS
   proxy server (same as for stable collectd container)

Build collectd-experimental container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ cd <BAROMETER_REPO_DIR>
    $ sudo docker build -t opnfv/barometer-collectd-experimental \
     --build-arg http_proxy=`echo $http_proxy` \
     --build-arg https_proxy=`echo $https_proxy` \
     --network=host -f docker/barometer-collectd-experimental/Dockerfile .

.. note::
   For `barometer-collectd-latest` and `barometer-collectd-experimental` containers
   proxy parameters should be passed only if system is behind an HTTP or HTTPS
   proxy server (same as for stable collectd container)

Run the collectd stable docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

   $ cd <BAROMETER_REPO_DIR>
   $ sudo docker run -ti --net=host -v \
   `pwd`/src/collectd/collectd_sample_configs:/opt/collectd/etc/collectd.conf.d \
   -v /var/run:/var/run -v /tmp:/tmp -v /sys/fs/resctrl:/sys/fs/resctrl \
   --privileged opnfv/barometer-collectd

.. note::
   The docker collectd image contains configuration for all the collectd
   plugins. In the command above we are overriding
   /opt/collectd/etc/collectd.conf.d by mounting a host directory
   src/collectd/collectd_sample_configs that contains only the sample
   configurations we are interested in running.

   *If some dependencies for plugins listed in configuration directory
   aren't met, then collectd startup may fail(collectd tries to
   initialize plugins configurations for all given config files that can
   be found in shared configs directory and may fail if some dependency
   is missing).*

   If `DPDK` or `RDT` can't be installed on host, then corresponding config
   files should be removed from shared configuration directory
   (`<BAROMETER_REPO_DIR>/src/collectd/collectd_sample_configs/`) prior
   to starting barometer-collectd container. By example: in case of missing
   `DPDK` functionality on the host, `dpdkstat.conf` and `dpdkevents.conf`
   should be removed.

   Sample configurations can be found at:
   https://github.com/opnfv/barometer/tree/master/src/collectd/collectd_sample_configs

   List of barometer-collectd dependencies on host for various plugins
   can be found at:
   https://wiki.opnfv.org/display/fastpath/Barometer-collectd+host+dependencies

   The Resource Control file system (/sys/fs/resctrl) can be bound from host to
   container only if this directory exists on the host system. Otherwise omit
   the '-v /sys/fs/resctrl:/sys/fs/resctrl' part in docker run command.
   More information about resctrl can be found at:
   https://github.com/intel/intel-cmt-cat/wiki/resctrl

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

Run the barometer-collectd-latest docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Run command for `barometer-collectd-latest` container is very similar to command
used for stable container - the only differences are name of the image
and location of the sample configuration files(as different version of collectd
plugins requiring different configuration files)


.. code:: bash

   $ cd <BAROMETER_REPO_DIR>
   $ sudo docker run -ti --net=host -v \
   `pwd`/src/collectd/collectd_sample_configs-latest:/opt/collectd/etc/collectd.conf.d \
   -v /var/run:/var/run -v /tmp:/tmp -v /sys/fs/resctrl:/sys/fs/resctrl \
   --privileged opnfv/barometer-collectd-latest

.. note::
   Barometer collectd docker images are sharing some directories with host
   (e.g. /tmp) therefore only one of collectd barometer flavors can be run
   at a time. In other words, if you want to try `barometer-collectd-latest` or
   `barometer-collectd-experimental` image, please stop instance of
   `barometer-collectd(stable)` image first.

   The Resource Control file system (/sys/fs/resctrl) can be bound from host to
   container only if this directory exists on the host system. Otherwise omit
   the '-v /sys/fs/resctrl:/sys/fs/resctrl' part in docker run command.
   More information about resctrl can be found at:
   https://github.com/intel/intel-cmt-cat/wiki/resctrl

Run the barometer-collectd-experimental docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Barometer-collectd-experimental container shares default configuration files
with 'barometer-collectd-latest' equivalent but some of experimental pull
requests may require modified configuration. Additional configuration files that
are required specifically by experimental container can be found in
`docker/barometer-collectd-experimental/experimental-configs/`
directory. Content of this directory (all \*.conf files) should be copied to
`src/collectd/collectd_sample_configs-latest` directory before first run of
experimental container.

.. code:: bash

   $ cd <BAROMETER_REPO_DIR>
   $ cp docker/barometer-collectd-experimental/experimental-configs/*.conf \
     src/collectd/collectd_sample_configs-latest

When configuration files are up to date for experimental container, it can be
launched using following command (almost identical to run-command for
``latest`` collectd container)

.. code:: bash

   $ cd <BAROMETER_REPO_DIR>
   $ sudo docker run -ti --net=host -v \
   `pwd`/src/collectd/collectd_sample_configs-latest:/opt/collectd/etc/collectd.conf.d \
   -v /var/run:/var/run -v /tmp:/tmp -v /sys/fs/resctrl:/sys/fs/resctrl --privileged \
   opnfv/barometer-collectd-experimental

.. note::
   The Resource Control file system (/sys/fs/resctrl) can be bound from host to
   container only if this directory exists on the host system. Otherwise omit
   the '-v /sys/fs/resctrl:/sys/fs/resctrl' part in docker run command.
   More information about resctrl can be found at:
   https://github.com/intel/intel-cmt-cat/wiki/resctrl


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
   `Run the Influxdb and Grafana Images`_

Build InfluxDB docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build influxdb image from Dockerfile

.. code:: bash

  $ cd barometer/docker/barometer-influxdb
  $ sudo docker build -t opnfv/barometer-influxdb --build-arg http_proxy=`echo $http_proxy` \
    --build-arg https_proxy=`echo $https_proxy` --network=host -f Dockerfile .

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: bash

   $ sudo docker run -tid -v /var/lib/influxdb:/var/lib/influxdb --net=host\
    --name bar-influxdb opnfv/barometer-influxdb

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

When both collectd and InfluxDB containers are located
on the same host, then no additional configuration have to be added and you
can proceed directly to `Run the Grafana docker image`_ section.

Modify collectd to support InfluxDB on another host
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If InfluxDB and collectd containers are located on separate hosts, then
additional configuration have to be done in ``collectd`` container - it
normally sends data using network plugin to 'localhost/127.0.0.1' therefore
changing output location is required:

1. Stop and remove running bar-collectd container (if it is running)

   .. code:: bash

      $ sudo docker ps #to get collectd container name
      $ sudo docker rm -f <COLLECTD_CONTAINER_NAME>

2. Go to location where shared collectd config files are stored

   .. code:: bash

      $ cd <BAROMETER_REPO_DIR>
      $ cd src/collectd/collectd_sample_configs

3. Edit content of ``network.conf`` file.
   By default this file looks like that:

   .. code::

      LoadPlugin  network
      <Plugin network>
      Server "127.0.0.1" "25826"
      </Plugin>

   ``127.0.0.1`` string has to be replaced with the IP address of host where
   InfluxDB container is running (e.g. ``192.168.121.111``). Edit this using your
   favorite text editor.

4. Start again collectd container like it is described in
   `Run the collectd stable docker image`_ chapter

   .. code:: bash

      $ cd <BAROMETER_REPO_DIR>
      $ sudo docker run -ti --name bar-collectd --net=host -v \
      `pwd`/src/collectd/collectd_sample_configs:/opt/collectd/etc/collectd.conf.d \
      -v /var/run:/var/run -v /tmp:/tmp --privileged opnfv/barometer-collectd

Now collectd container will be sending data to InfluxDB container located on
remote Host pointed by IP configured in step 3.

Run the Grafana docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting to an influxdb instance running on local system and adding own custom dashboards

.. code:: bash

   $ cd <BAROMETER_REPO_DIR>
   $ sudo docker run -tid -v /var/lib/grafana:/var/lib/grafana \
     -v ${PWD}/docker/barometer-grafana/dashboards:/opt/grafana/dashboards \
     --name bar-grafana --net=host opnfv/barometer-grafana

Connecting to an influxdb instance running on remote system with hostname of someserver and IP address
of 192.168.121.111

.. code:: bash

   $ sudo docker run -tid -v /var/lib/grafana:/var/lib/grafana --net=host -e \
     influxdb_host=someserver --add-host someserver:192.168.121.111 --name \
     bar-grafana opnfv/barometer-grafana

Check your docker image is running

.. code:: bash

   sudo docker ps

To make some changes when the container is running run:

.. code:: bash

   sudo docker exec -ti <CONTAINER ID> /bin/bash

Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin

Cleanup of influxdb/grafana configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When user wants to remove current grafana and influxdb configuration,
folowing actions have to be performed

1. Stop and remove running influxdb and grafana containers

.. code:: bash

   sudo docker rm -f bar-grafana bar-influxdb

2. Remove shared influxdb and grafana folders from the Host

.. code:: bash

   sudo rm -rf /var/lib/grafana
   sudo rm -rf /var/lib/influxdb

.. note::
   Shared folders are storing configuration of grafana and influxdb
   containers. In case of changing influxdb or grafana configuration
   (e.g. moving influxdb to another host) it is good to perform cleanup
   on shared folders to not affect new setup with an old configuration.

Build and Run VES and Kafka Docker Images
-----------------------------------------

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
   `Run Kafka Docker Image`_

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

Run VES Test Collector application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

VES Test Collector application can be used for displaying platform
wide metrics that are collected by barometer-ves container.
Setup instructions are located in: :ref:`Setup VES Test Collector`

Build and Run DMA and Redis Docker Images
-----------------------------------------

Download DMA docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you wish to use pre-built barometer project's DMA images, you can pull the
images from https://hub.docker.com/r/opnfv/barometer-dma/

.. note::
   If your preference is to build images locally please see sections `Build DMA Docker Image`_

.. code:: bash

    $ docker pull opnfv/barometer-dma

.. note::
   If you have pulled the pre-built images there is no requirement to complete steps outlined
   in sections `Build DMA Docker Image`_ and you can proceed directly to section
   `Run DMA Docker Image`_

Build DMA docker image
^^^^^^^^^^^^^^^^^^^^^^

Build DMA docker image:

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
^^^^^^^^^^^^^^^^^^^^^^

.. note::
   Before running DMA, Redis must be running.

Run Redis docker image:

.. code:: bash

   $ sudo docker run -tid -p 6379:6379 --name barometer-redis redis

Check your docker image is running

.. code:: bash

   sudo docker ps

Run DMA docker image
^^^^^^^^^^^^^^^^^^^^
.. note::

Run DMA docker image with default configuration

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

References
^^^^^^^^^^
.. [1] https://docs.docker.com/config/daemon/systemd/#httphttps-proxy
.. [2] https://docs.docker.com/engine/install/centos/#install-using-the-repository
.. [3] https://docs.docker.com/engine/userguide/


