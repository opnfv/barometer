plugin-collectd-ceilometer
=========================

Plugin description
Installs collectd-ceilometer on compute via a fuel plugin.

Requirements
------------

| Requirement                      | Version/Comment |
|----------------------------------|-----------------|
| Mirantis OpenStack compatibility | 10.0            |


Documents
---------

1. https://wiki.openstack.org/wiki/Fuel
2. https://wiki.openstack.org/wiki/Fuel/Plugins

Build/Deploy/Verify
-------------------

step 1, 2, 3 may be bypassed if fuel plugin is installed from /opt/opnfv in fuel@opnfv.

1) install fuel plugin builder
    sudo apt-get install -y ruby-dev rubygems-integration python-pip rpm createrepo dpkg-dev
    sudo gem install fpm
    sudo pip install fuel-plugin-builder

2) build plugin
    fpb --build <plugin-dir>
    e.g.: fpb --build fastpathmetrics/src/fuel-plugin

3) copy plugin rpm to fuel master
	e.g. scp fuel-plugin-collectd-ceilometer-0.9-0.9.0-1.noarch.rpm  <user>@<server-name>:~/

4) install plugin
	fuel plugins --install <plugin-name>.rpm

5) prepare fuel environment
  a) enable ceilometer service
    go to settings/openstack services
    enable ceilometer plugin with checkbox
  b) enable collectd-ceilometer
    go to settings/other
    enable collectd-ceilometer plugin with checkbox
  c) save settings

6) add nodes to environment

7) deploy

8) verify
SSH to openstack controller node:
    source openrc
    ceilometer sample-list --meter interface.if_packets
