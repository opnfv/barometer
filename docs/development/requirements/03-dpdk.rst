.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket, Intel Corporation and others.

DPDK Enhancements
==================
This section will discuss the Barometer features that were integrated with DPDK.

Measuring Telco Traffic and Performance KPIs
--------------------------------------------
This section will discuss the Barometer features that enable Measuring Telco Traffic
and Performance KPIs.

.. Figure:: stats_and_timestamps.png

   Measuring Telco Traffic and Performance KPIs

* The very first thing Barometer enabled was a call-back API in DPDK and an
  associated application that used the API to demonstrate how to timestamp
  packets and measure packet latency in DPDK (the sample app is called
  rxtx_callbacks). This was upstreamed to DPDK 2.0 and is represented by
  the interfaces 1 and 2 in Figure 1.2.

* The second thing Barometer implemented in DPDK is the extended NIC statistics API,
  which exposes NIC stats including error stats to the DPDK user by reading the
  registers on the NIC. This is represented by interface 3 in Figure 1.2.

  * For DPDK 2.1 this API was only implemented for the ixgbe (10Gb) NIC driver,
    in association with a sample application that runs as a DPDK secondary
    process and retrieves the extended NIC stats.

  * For DPDK 2.2 the API was implemented for igb, i40e and all the Virtual
    Functions (VFs) for all drivers.

  * For DPDK 16.07 the API migrated from using string value pairs to using id
    value pairs, improving the overall performance of the API.

Monitoring DPDK interfaces
--------------------------
With the features Barometer enabled in DPDK to enable measuring Telco traffic and
performance KPIs, we can now retrieve NIC statistics including error stats and
relay them to a DPDK user. The next step is to enable monitoring of the DPDK
interfaces based on the stats that we are retrieving from the NICs, by relaying
the information to a higher level Fault Management entity. To enable this Barometer
has been enabling a number of plugins for collectd.

DPDK Keep Alive description
---------------------------
SFQM aims to enable fault detection within DPDK, the very first feature to
meet this goal is the DPDK Keep Alive Sample app that is part of DPDK 2.2.

DPDK Keep Alive or KA is a sample application that acts as a heartbeat/watchdog
for DPDK packet processing cores, to detect application thread failure. The
application supports the detection of ‘failed’ DPDK cores and notification to a
HA/SA middleware. The purpose is to detect Packet Processing Core fails (e.g.
infinite loop) and ensure the failure of the core does not result in a fault
that is not detectable by a management entity.

.. Figure:: dpdk_ka.png

   DPDK Keep Alive Sample Application

Essentially the app demonstrates how to detect 'silent outages' on DPDK packet
processing cores. The application can be decomposed into two specific parts:
detection and notification.

* The detection period is programmable/configurable but defaults to 5ms if no
  timeout is specified.
* The Notification support is enabled by simply having a hook function that where this
  can be 'call back support' for a fault management application with a compliant
  heartbeat mechanism.

DPDK Keep Alive Sample App Internals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This section provides some explanation of the The Keep-Alive/'Liveliness'
conceptual scheme as well as the DPDK Keep Alive App. The initialization and
run-time paths are very similar to those of the L2 forwarding application (see
`L2 Forwarding Sample Application (in Real and Virtualized Environments)`_ for more
information).

There are two types of cores: a Keep Alive Monitor Agent Core (master DPDK core)
and Worker cores (Tx/Rx/Forwarding cores). The Keep Alive Monitor Agent Core
will supervise worker cores and report any failure (2 successive missed pings).
The Keep-Alive/'Liveliness' conceptual scheme is:

* DPDK worker cores mark their liveliness as they forward traffic.
* A Keep Alive Monitor Agent Core runs a function every N Milliseconds to
  inspect worker core liveliness.
* If keep-alive agent detects time-outs, it notifies the fault management
  entity through a call-back function.

**Note:**  Only the worker cores state is monitored. There is no mechanism or agent
to monitor the Keep Alive Monitor Agent Core.

DPDK Keep Alive Sample App Code Internals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following section provides some explanation of the code aspects that are
specific to the Keep Alive sample application.

The heartbeat functionality is initialized with a struct rte_heartbeat and the
callback function to invoke in the case of a timeout.

.. code:: c

    rte_global_keepalive_info = rte_keepalive_create(&dead_core, NULL);
    if (rte_global_hbeat_info == NULL)
        rte_exit(EXIT_FAILURE, "keepalive_create() failed");

The function that issues the pings hbeat_dispatch_pings() is configured to run
every check_period milliseconds.

.. code:: c

    if (rte_timer_reset(&hb_timer,
            (check_period * rte_get_timer_hz()) / 1000,
            PERIODICAL,
            rte_lcore_id(),
            &hbeat_dispatch_pings, rte_global_keepalive_info
            ) != 0 )
        rte_exit(EXIT_FAILURE, "Keepalive setup failure.\n");

The rest of the initialization and run-time path follows the same paths as the
the L2 forwarding application. The only addition to the main processing loop is
the mark alive functionality and the example random failures.

.. code:: c

    rte_keepalive_mark_alive(&rte_global_hbeat_info);
    cur_tsc = rte_rdtsc();

    /* Die randomly within 7 secs for demo purposes.. */
    if (cur_tsc - tsc_initial > tsc_lifetime)
    break;

The rte_keepalive_mark_alive() function simply sets the core state to alive.

.. code:: c

    static inline void
    rte_keepalive_mark_alive(struct rte_heartbeat *keepcfg)
    {
        keepcfg->state_flags[rte_lcore_id()] = 1;
    }

Keep Alive Monitor Agent Core Monitoring Options
The application can run on either a host or a guest. As such there are a number
of options for monitoring the Keep Alive Monitor Agent Core through a Local
Agent on the compute node:

         ======================  ==========  =============
          Application Location     DPDK KA     LOCAL AGENT
         ======================  ==========  =============
                  HOST               X        HOST/GUEST
                  GUEST              X        HOST/GUEST
         ======================  ==========  =============


For the first implementation of a Local Agent SFQM will enable:

         ======================  ==========  =============
          Application Location     DPDK KA     LOCAL AGENT
         ======================  ==========  =============
                  HOST               X           HOST
         ======================  ==========  =============

Through extending the dpdkstat plugin for collectd with KA functionality, and
integrating the extended plugin with Monasca for high performing, resilient,
and scalable fault detection.

.. _L2 Forwarding Sample Application (in Real and Virtualized Environments): http://doc.dpdk.org/guides/sample_app_ug/l2_forward_real_virtual.html
