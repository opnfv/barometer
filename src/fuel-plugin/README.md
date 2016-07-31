plugin-collectd-ceilometer
=========================

Plugin description
Installs collectd-ceilometer on compute via a fuel plugin.

Requirements
------------

| Requirement                      | Version/Comment |
|----------------------------------|-----------------|
| Mirantis OpenStack compatibility | 9.0             |


Documents
---------

1. https://wiki.openstack.org/wiki/Fuel
2. https://wiki.openstack.org/wiki/Fuel/Plugins

Build/Deploy/Verify
-------------------

1) install fuel plugin builder (fpb)
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
	on fuel dashboard, go to settings/other
	enable collectd-ceilometer plugin with checkbox
	save settings

6) add nodes to environment

7) deploy

8) verify
SSH to openstack controller node:
    source openrc
    ceilometer sample-list --meter interface.if_packets

9) known issues

a) connection aborted
  root@node-11:~# ceilometer sample-list --meter interface.if_packets
('Connection aborted.', BadStatusLine("''",))

  workaround:
  root@node-11:~# sudo service ceilometer-api restart

b) Service Unavailable
  root@node-11:~# ceilometer sample-list --meter interface.if_packets
Service Unavailable (HTTP 503)

  workaround:
  root@node-11:~# sudo service ceilometer-api restart
