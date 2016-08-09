.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

Features to Date
================
This section provides a summary of the features implemented to date and their
relevant upstream projects.

.. Figure:: Features_to_date1.png

   SFQM features to date

.. Figure:: Features_to_date2.png

   SFQM features to date cont.

Please note the timeline denotes DPDK releases.

Release B
=========
The features implemented for OPNFV release B in DPDK include:

* Callback API to enable TX/RX timestamping to measure latency through DPDK.
* Extended NIC statistics API for 1GB, 10GB and 40GB NICs to expose detailed
  statistics for DPDK interfaces in addition to the overall aggregate statistics.
* DPDK Keep Alive.

Release C
=========
The features implemented for OPNFV release C include:

* DPDK extended NIC stats API improvement; migrate from key value pairs to
  using id value pairs.
* DPDK Keep Alive improvement, so that core status is exposed through a posix
  shared memory object.
* collectd dpdkstat plugin that can retrieve DPDK interface statistics.
* collectd ceilometer plugin that can publish any statistics collected by
  collectd to ceilometer.
* Fuel plugin support for the collectd ceilometer plugin for OPNFV.
