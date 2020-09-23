.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) <optionally add copywriters name>
.. _barometer-oneclick-userguide:

=======================================
OPNFV Barometer One Click Install Guide
=======================================

.. contents::
   :depth: 3
   :local:

The intention of this user guide is to outline how to use the ansible
playbooks for a one click installation of Barometer. A more in-depth
installation guide is available with the
:ref:`Docker user guide <barometer-docker-userguide>`.


One Click Install with Ansible
------------------------------


Proxy for package manager on host
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
   This step has to be performed only if host is behind HTTP/HTTPS proxy

Proxy URL have to be set in dedicated config file

1. CentOS - ``/etc/yum.conf``

.. code:: bash

    proxy=http://your.proxy.domain:1234

2. Ubuntu - ``/etc/apt/apt.conf``

.. code:: bash

    Acquire::http::Proxy "http://your.proxy.domain:1234"

After update of config file, apt mirrors have to be updaited via
``apt-get update``

.. code:: bash

    $ sudo apt-get update

Proxy environment variables (for docker and pip)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
   This step has to be performed only if host is behind HTTP/HTTPS proxy

Configuring proxy for packaging system is not enough, also some proxy
environment variables have to be set in the system before ansible scripts
can be started.
Barometer configures docker proxy automatically via ansible task as a part
of *one click install* process - user only has to provide proxy URL using common
shell environment variables and ansible will automatically configure proxies
for docker(to be able to fetch barometer images). Another component used by
ansible (e.g. pip is used for downloading python dependencies) will also benefit
from setting proxy variables properly in the system.

Proxy variables used by ansible One Click Install:
   * ``http_proxy``
   * ``https_proxy``
   * ``ftp_proxy``
   * ``no_proxy``

Variables mentioned above have to be visible for superuser (because most
actions involving ``ansible-barometer`` installation require root privileges).
Proxy variables are commonly defined in ``/etc/environment`` file (but any other
place is good as long as variables can be seen by commands using ``su``).

Sample proxy configuration in ``/etc/environment``:

.. code:: bash

    http_proxy=http://your.proxy.domain:1234
    https_proxy=http://your.proxy.domain:1234
    ftp_proxy=http://your.proxy.domain:1234
    no_proxy=localhost

Install Ansible
^^^^^^^^^^^^^^^
.. note::
   * sudo permissions or root access are required to install ansible.
   * ansible version needs to be 2.4+, because usage of import/include statements

The following steps have been verified with Ansible 2.6.3 on Ubuntu 16.04 and 18.04.
To install Ansible 2.6.3 on Ubuntu:

.. code:: bash

    $ sudo apt-get install python
    $ sudo apt-get install python-pip
    $ sudo -H pip install 'ansible==2.6.3'
    $ sudo apt-get install git

The following steps have been verified with Ansible 2.6.3 on Centos 7.5.
To install Ansible 2.6.3 on Centos:

.. code:: bash

    $ sudo yum install python
    $ sudo yum install epel-release
    $ sudo yum install python-pip
    $ sudo -H pip install 'ansible==2.6.3'
    $ sudo yum install git

.. note::
   When using multi-node-setup, please make sure that ``python`` package is
   installed on all of the target nodes (ansible during 'Gathering facts'
   phase is using ``python2`` and it may not be installed by default on some
   distributions - e.g. on Ubuntu 16.04 it has to be installed manually)

Clone barometer repo
^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ git clone https://gerrit.opnfv.org/gerrit/barometer
    $ cd barometer/docker/ansible

Edit inventory file
^^^^^^^^^^^^^^^^^^^
Edit inventory file and add hosts:
``$barometer_dir/docker/ansible/default.inv``

.. code:: bash

    [collectd_hosts]
    localhost

    [collectd_hosts:vars]
    install_mcelog=true
    insert_ipmi_modules=true
    #to use master or experimental container set the collectd flavor below
    #possible values: stable|master|experimental
    flavor=stable

    [influxdb_hosts]
    #hostname or ip must be used.
    #using localhost will cause issues with collectd network plugin.
    #hostname

    [grafana_hosts]
    #NOTE: As per current support, Grafana and Influxdb should be same host.
    #hostname

    [prometheus_hosts]
    #localhost

    [zookeeper_hosts]
    #NOTE: currently one zookeeper host is supported
    #hostname

    [kafka_hosts]
    #hostname

    [ves_hosts]
    #hostname

Change localhost to different hosts where neccessary.
Hosts for influxdb and grafana are required only for ``collectd_service.yml``.
Hosts for zookeeper, kafka and ves are required only for ``collectd_ves.yml``.

.. note::
   Zookeeper, Kafka and VES need to be on the same host, there is no
   support for multi node setup.

To change host for kafka edit ``kafka_ip_addr`` in
``./roles/config_files/vars/main.yml``.

Additional plugin dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default ansible will try to fulfill dependencies for ``mcelog`` and
``ipmi`` plugin. For ``mcelog`` plugin it installs mcelog daemon. For ipmi it
tries to insert ``ipmi_devintf`` and ``ipmi_si`` kernel modules.
This can be changed in inventory file with use of variables ``install_mcelog``
and ``insert_ipmi_modules``, both variables are independent:

.. code:: bash

    [collectd_hosts:vars]
    install_mcelog=false
    insert_ipmi_modules=false

.. note::
   On Ubuntu 18.04 the deb package for mcelog daemon is not available in official
   Ubuntu repository. In that case ansible scripts will try to download, make and
   install the daemon from mcelog git repository.

Configure ssh keys
^^^^^^^^^^^^^^^^^^

Generate ssh keys if not present, otherwise move onto next step.
ssh keys are required for Ansible to connect the host you use for Barometer Installation.

.. code:: bash

    $ sudo ssh-keygen

Copy ssh key to all target hosts. It requires to provide root password.
The example is for ``localhost``.

.. code:: bash

    $ sudo -i
    $ ssh-copy-id root@localhost

Verify that key is added and password is not required to connect.

.. code:: bash

    $ sudo ssh root@localhost

.. note::
   Keys should be added to every target host and [localhost] is only used as an
   example. For multinode installation keys need to be copied for each node:
   [collectd_hostname], [influxdb_hostname] etc.

Download and run Collectd+Influxdb+Grafana containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The One Click installation features easy and scalable deployment of Collectd,
Influxdb and Grafana containers using Ansible playbook. The following steps goes
through more details.

.. code:: bash

    $ sudo -H ansible-playbook -i default.inv collectd_service.yml

Check the three containers are running, the output of ``docker ps`` should be similar to:

.. code:: bash

    $ sudo docker ps
    CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS               NAMES
    a033aeea180d        opnfv/barometer-grafana    "/run.sh"                9 days ago          Up 7 minutes                            bar-grafana
    1bca2e4562ab        opnfv/barometer-influxdb   "/entrypoint.sh in..."   9 days ago          Up 7 minutes                            bar-influxdb
    daeeb68ad1d5        opnfv/barometer-collectd   "/run_collectd.sh ..."   9 days ago          Up 7 minutes                            bar-collectd

To make some changes when a container is running run:

.. code:: bash

    $ sudo docker exec -ti <CONTAINER ID> /bin/bash

Connect to ``<host_ip>:3000`` with a browser and log into Grafana: admin/admin.
For short introduction please see the:
`Grafana guide <http://docs.grafana.org/guides/getting_started/>`_.

The collectd configuration files can be accessed directly on target system in
``/opt/collectd/etc/collectd.conf.d``. It can be used for manual changes or
enable/disable plugins. If configuration has been modified it is required to
restart collectd:

.. code:: bash

    $ sudo docker restart bar-collectd

Download and run collectd+kafka+ves containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    $ sudo ansible-playbook -i default.inv collectd_ves.yml

Check the containers are running, the output of ``docker ps`` should be similar to:

.. code:: bash

    $ sudo docker ps
    CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS                     PORTS               NAMES
    29035be2dab5        zookeeper:3.4.11           "/docker-entrypoint._"   7 minutes ago       Up 7 minutes                                   bar-zookeeper
    eb8bba3c0b76        opnfv/barometer-ves        "./start_ves_app.s..."   6 minutes ago       Up 6 minutes                                   bar-ves
    86702a96a68c        opnfv/barometer-kafka      "/src/start_kafka.sh"    6 minutes ago       Up 6 minutes                                   bar-kafka
    daeeb68ad1d5        opnfv/barometer-collectd   "/run_collectd.sh ..."   6 minutes ago       Up 6 minutes                                   bar-collectd


To make some changes when a container is running run:

.. code:: bash

    $ sudo docker exec -ti <CONTAINER ID> /bin/bash

List of default plugins for collectd container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
   From Jerma release, the supported dpdk version is 19.11

   If you would like to use v18.11, Do the following changes:
    1.Update the dpdk version to v18.11 in <barometer>/src/package-list.mk
    2.Replace all 'common_linux' string with 'common_linuxapp' in <barometer>/src/dpdk/Makefile
   
   If you would like to downgrade to a version lower than v18.11, Do the following changes:
    1.Update the dpdk version to a version lower than v18.11(Eg:- v16.11) in <barometer>/src/package-list.mk
    2.Replace all 'common_linux' string with 'common_linuxapp' in <barometer>/src/dpdk/Makefile
    3.Change the Makefile path from '(WORKDIR)/kernel/linux/kni/Makefile' to (WORKDIR)/lib/librte_eal/linuxapp/kni/Makefile in '(WORK_DIR)/src/dpdk/Makefile'.

By default the collectd is started with default configuration which includes
the following plugins:
    * ``csv``, ``contextswitch``, ``cpu``, ``cpufreq``, ``df``, ``disk``,
      ``ethstat``, ``ipc``, ``irq``, ``load``, ``memory``, ``numa``,
      ``processes``, ``swap``, ``turbostat``, ``uuid``, ``uptime``, ``exec``,
      ``hugepages``, ``intel_pmu``, ``ipmi``, ``write_kafka``, ``logfile``,
      ``mcelog``, ``network``, ``intel_rdt``, ``rrdtool``, ``snmp_agent``,
      ``syslog``, ``virt``, ``ovs_stats``, ``ovs_events``, ``dpdkevents``,
      ``dpdkstat``, ``dpdk_telemetry``

.. note::
   Some of the plugins are loaded depending on specific system requirements and can be omitted if
   dependency is not met, this is the case for:
   * ``hugepages``, ``ipmi``, ``mcelog``, ``intel_rdt``, ``virt``, ``ovs_stats``, ``ovs_events`` 

List and description of tags used in ansible scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tags can be used to run a specific part of the configuration without running
the whole playbook. To run a specific parts only:

.. code:: bash

    $ sudo ansible-playbook -i default.inv collectd_service.yml --tags "syslog,cpu,uuid"

To disable some parts or plugins:

.. code:: bash

    $ sudo ansible-playbook -i default.inv collectd_service.yml --skip-tags "en_default_all,syslog,cpu,uuid"

List of available tags:

``install_docker``
  Install docker and required dependencies with package manager.

``add_docker_proxy``
  Configure proxy file for docker service if proxy is set on host environment.

``rm_config_dir``
  Remove collectd config files.

``copy_additional_configs``
  Copy additional configuration files to target system. Path to additional
  configuration is stored in
  ``$barometer_dir/docker/ansible/roles/config_files/vars/main.yml`` as
  ``additional_configs_path``.

``en_default_all``
  Set of default read plugins: ``contextswitch``, ``cpu``, ``cpufreq``, ``df``,
  ``disk``, ``ethstat``, ``ipc``, ``irq``, ``load``, ``memory``, ``numa``,
  ``processes``, ``swap``, ``turbostat``, ``uptime``.

``plugins tags``
  The following tags can be used to enable/disable plugins: ``csv``,
  ``contextswitch``, ``cpu``, ``cpufreq``, ``df``, ``disk,`` ``ethstat``,
  ``ipc``, ``irq``, ``load``, ``memory``, ``numa``, ``processes``, ``swap``,
  ``turbostat``, ``uptime``, ``exec``, ``hugepages``, ``ipmi``, ``kafka``,
  ``logfile``, ``mcelogs``, ``n``etwork``,`` ``pmu``, ``rdt``, ``rrdtool``,
  ``snmp``, ``syslog``, ``virt``, ``ovs_stats``, ``ovs_events``, ``uuid``,
  ``dpdkevents``, ``dpdkstat``, ``dpdk_telemetry``.

