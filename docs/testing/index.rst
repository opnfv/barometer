.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket and others

==============================
Anuket Barometer testing guide
==============================

This document will describe how to use different tests in this repo.

There are a number of tools and scripts in Barometer that can be used for testing, whether that is during development, building, code reviews, or run regularly in CI.
Some of the tests are automated, and cover building collectd, others cover particular plugins.

.. TODO: This guide should also include how to manually verify that collectd plugins are working as expected.

.. TODO: There might be some troubleshooting guide in here too.

Porting collectd to version 6
=============================

Thre is an ansible playbook for building and running collectd 5 and 6 together to compare the collected metrics.
This is intended to help test porting from collectd 5 to 6, and confirm equivalency across the versions.

The playbook will::

  * build collectd-6, collectd-latest and flask app containers
  * generate a set of collectd configs
  * launch the collectd-6, collectd-latest with the generated configs
  * run the flask app which has a http server that receives metrics from
    collectd v5 and collectd v6
  * display the received metrics from both versions of collectd
    Collectd v5 shows PUTVAL
    Collectd v6 shows PUTMETRIC

To run this comparison, use the following command::

  $ cd docker/ansible/
  $ sudo ansible-playbook -i default.inv collectd6-test.yml

The playbook takes the following parameters:

  * PR (optional)
    The PRID for an upstream collectd pull request that will be
    passed to the collectd 6 container build

  * plugin (optional)
    The name of the plugin that is bneing ported
    This will filter the received metrics to show the value passed.

To run the playbook with these configs, pass the extra var to ansible::

  sudo ansible-playbook -i default.inv -e PR=<PR_ID> -e plugin=<plugin_name> collectd6-test.yml

The metrics can then be viewed by inspecting the container logs or attaching to the container to view the output::

  $ docker attach <webserver-container>
  $ #OR
  $ docker logs <webserver-container>

Metrics from collectd 5 will appear preceeded with ``PUTVAL``, and metrics from collectd 6 will appear preceeded by ``PUTMETRIC``.

::

  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-mm-2048Kb/vmpage_number-free interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-mm-2048Kb/vmpage_number-used interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-mm-1048576Kb/vmpage_number-free interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-mm-1048576Kb/vmpage_number-used interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-node0-2048Kb/vmpage_number-free interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-node0-2048Kb/vmpage_number-used interval=10.000 1629466502.664:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-node0-1048576Kb/vmpage_number-used interval=10.000 1629466502.665:0
  PUTVAL fbae30cc-2f20-11b2-a85c-819293100691/hugepages-node0-1048576Kb/vmpage_number-free interval=10.000 1629466502.665:0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.807 interval=10.000 label:hugepages="mm-2048Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="free" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.807 interval=10.000 label:hugepages="mm-2048Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="used" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.808 interval=10.000 label:hugepages="mm-1048576Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="free" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.808 interval=10.000 label:hugepages="node0-2048Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="free" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.808 interval=10.000 label:hugepages="node0-2048Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="used" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.809 interval=10.000 label:hugepages="node0-1048576Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="free" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.809 interval=10.000 label:hugepages="node0-1048576Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="used" 0
  PUTMETRIC collectd_hugepages_vmpage_number type=GAUGE time=1629466501.808 interval=10.000 label:hugepages="mm-1048576Kb" label:instance="fbae30cc-2f20-11b2-a85c-819293100691" label:type="used" 0
