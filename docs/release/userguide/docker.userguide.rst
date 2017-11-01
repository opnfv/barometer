.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>

===================================
OPNFV Barometer Docker User Guide
===================================

.. contents::
   :depth: 3
   :local:

Barometer docker image description
-----------------------------------
.. Describe the specific features and how it is realised in the scenario in a brief manner
.. to ensure the user understand the context for the user guide instructions to follow.

The intention of this user guide is to outline how to install and test the
barometer docker image that can be built from the Dockerfile available in the
barometer repository.

.. note::
   The Dockerfile is available in the docker/ directory in the barometer repo.
   The Dockerfile builds a CentOS 7 docker image.

The barometer docker image gives you a collectd installation that includes all
the barometer plugins.

.. note::
   The container MUST be run as a privileged container.

Collectd is a daemon which collects system performance statistics periodically
and provides a variety of mechanisms to publish the collected metrics. It
supports more than 90 different input and output plugins. Input plugins
retrieve metrics and publish them to the collectd deamon, while output plugins
publish the data they receive to an end point. collectd also has infrastructure
to support thresholding and notification.

Barometer docker image has enabled the following collectd plugins (in addition
to the standard collectd plugins):

* hugepages plugin
* Open vSwitch events Plugin
* Open vSwitch stats Plugin
* mcelog plugin
* PMU plugin
* RDT plugin
* virt
* SNMP Agent

Plugins and third party applications in Barometer repository that will be available in the
docker image:

* Open vSwitch PMD stats
* ONAP VES application
* gnocchi plugin
* aodh plugin
* Legacy/IPMI


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

Build the barometer docker image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ cd barometer
    $ sudo docker build -t barometer_image --build-arg http_proxy=`echo $http_proxy` \
      --build-arg https_proxy=`echo $https_proxy` -f docker/Dockerfile .

.. note::
   In the above mentioned ``docker build`` command, http_proxy & https_proxy arguments needs to be passed only if system is behind an HTTP or HTTPS proxy server.

Check the docker images:

.. code:: bash

   $ sudo docker images

Output should contain a barometer image:

.. code::

   REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
   barometer_image     latest              05f2a3edd96b        3 hours ago         1.2GB
   centos              7                   196e0ce0c9fb        4 weeks ago         197MB
   centos              latest              196e0ce0c9fb        4 weeks ago         197MB
   hello-world         latest              05a3bd381fc2        4 weeks ago         1.84kB

Run the barometer docker image:

.. code:: bash

   $ sudo docker run -tid --net=host -v `pwd`/../src/collectd_sample_configs:/opt/collectd/etc/collectd.conf.d \
    -v /var/run:/var/run -v /tmp:/tmp --privileged barometer_image /run_collectd.sh

.. note::
  The docker barometer image contains configuration for all the collectd plugins. In the command
  above we are overriding /opt/collectd/etc/collectd.conf.d by mounting a host directory
  `pwd`/../src/collectd_sample_configs thta contains only the sample configurations we are interested
  in running.

To make some changes run:

.. code:: bash

   sudo docker exec -tid barometer_image /bin/bash

Check your docker image is running

.. code:: bash

   sudo docker ps

Build the influxdb + Grafana docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start by installing docker compose:

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

4. Run the get_types_db.sh script in barometer/docker

5. Run the docker containers:

.. code:: bash

  $ sudo docker-compose up -d

6. Check your docker images are running

.. code:: bash

   $ sudo docker ps
   
7. Run the script to create the CPU dashboard barometer/docker:

.. code:: bash

   $ ./configure_grafana.sh
   
8. Connect to <host_ip>:3000 with a browser and log into grafana: admin/admin

Testing the docker image
^^^^^^^^^^^^^^^^^^^^^^^^

TODO

References
^^^^^^^^^^^
.. [1] https://docs.docker.com/engine/admin/systemd/#httphttps-proxy
.. [2] https://docs.docker.com/engine/installation/linux/docker-ce/centos/#install-using-the-repository
.. [3] https://docs.docker.com/engine/userguide/

