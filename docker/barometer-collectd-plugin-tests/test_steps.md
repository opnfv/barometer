###############
 Running Tests
###############
The Barometer project leverages Collectd and contributes to the development of
various of its plugins. These tests in this folder aim to check the working of
the same.

=============
Dependencies
=============

* Docker 17.05+

===================
How the tests run
===================

The tests run in docker containers, they use a multi-stage build structure, as
highlighted by the names used the `Dockerfile.base` is the base container i.e a
CentOS 7 image along with the base dependencies and the `Dockerfile` inherits
this base and applies collectd and its plugins according to the PR it needs to
be tested for.

===========================
Steps to run tests locally
===========================

To create the Dockerfile which the test cases loaded:

``$cd \path\to\barometer``

#. Then run this command to build the base image:

   ``sudo docker build -t opnfv/barometer-collectd-tests-base --network=host \
   -f docker/barometer-collectd-plugin-tests/Dockerfile.base .``

#. Then build the collectd cases dockerfile on it with the command :

   ``sudo docker build -t opnfv/barometer-collectd-tests --network=host \
   -f docker/barometer-collectd-plugin-tests/Dockerfile --build-arg PR= 'PR to be applied' .``

#. Then run the container with :

   ``sudo docker run -ti --net=host -v \
 `pwd`/src/collectd/collectd_sample_configs-master:/opt/collectd/etc/collectd.conf.d -v \
/var/run:/var/run -v /tmp:/tmp -v \
 `pwd`/plugin_test:/tests --privileged opnfv/barometer-collectd-tests:latest
``

**or**

#. ``cd path/to/barometer/docker/barometer-collectd-plugin-tests``
#. ``chmod +x run_test.sh``
#. ``./run_test.sh {PR number}``

========
Output
========

Using the pytest framework we view the output of the test-cases.
