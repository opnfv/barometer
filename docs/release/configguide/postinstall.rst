.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Barometer post installation procedures
======================================
Add a brief introduction to the methods of validating the installation
according to this specific installer or feature.

Automated post installation activities
--------------------------------------
Describe specific post installation activities performed by the OPNFV
deployment pipeline including testing activities and reports. Refer to
the relevant testing guides, results, and release notes.

note: this section should be singular and derived from the test projects
once we have one test suite to run for all deploy tools.  This is not the
case yet so each deploy tool will need to provide (hopefully very simillar)
documentation of this.

Barometer post configuration procedures
--------------------------------------
The fuel plugin installs collectd and its plugins on compute nodes.
separate config files for each of the collectd plugins. These
configuration files can be found on the compute node @
`/etc/collectd/collectd.conf.d/` directory. Each collectd plugin will
have its own configuration file with a default configuration for each
plugin. You can override any of the plugin configurations, by modifying
the configuration file and restarting the collectd service on the compute node.

Platform components validation
---------------------------------
1. SSH to a compute node and ensure that the collectd service is running.

2. On the compute node, you need to inject a corrected memory error:

.. code:: bash

    $ git clone https://git.kernel.org/pub/scm/utils/cpu/mce/mce-inject.git
    $ cd mce-inject
    $ make
    $ modprobe mce-inject

Modify the test/corrected script to include the following:

.. code:: bash

    CPU 0 BANK 0
    STATUS 0xcc00008000010090
    ADDR 0x0010FFFFFFF

Inject the error:

.. code:: bash

    $ ./mce-inject < test/corrected

3. SSH to openstack controller node and query the ceilometer DB:

.. code:: bash

    $ source openrc
    $ ceilometer sample-list -m interface.if_packets
    $ ceilometer sample-list -m hugepages.vmpage_number
    $ ceilometer sample-list -m ovs_events.gauge
    $ ceilometer sample-list -m mcelog.errors

As you run each command above, you should see output similar to the examples below:

.. code:: bash
 | node-6.domain.tld-br-prv-link_status       | ovs_events.gauge | gauge | 1.0    | None | 2017-01-20T18:18:40 |
 | node-6.domain.tld-int-br-prv-link_status   | ovs_events.gauge | gauge | 1.0    | None | 2017-01-20T18:18:39 |
 | node-6.domain.tld-br-int-link_status       | ovs_events.gauge | gauge | 0.0    | None | 2017-01-20T18:18:39 |

 | node-6.domain.tld-mm-2048Kb-free    | hugepages.vmpage_number | gauge | 0.0    | None | 2017-01-20T18:17:12 |
 | node-6.domain.tld-mm-2048Kb-used    | hugepages.vmpage_number | gauge | 0.0    | None | 2017-01-20T18:17:12 |
 +-------------------------------------+-------------------------+-------+--------+------+---------------------+

 | bf05daca-df41-11e6-b097-5254006ed58e | node-6.domain.tld-SOCKET_0_CHANNEL_0_DIMM_any-uncorrected_memory_errors_in_24h   | mcelog.errors    | gauge | 0.0          | None    | 2017-01-20T18:53:34 |
 | bf05dacb-df41-11e6-b097-5254006ed58e | node-6.domain.tld-SOCKET_0_CHANNEL_any_DIMM_any-uncorrected_memory_errors_in_24h | mcelog.errors    | gauge | 0.0          | None    | 2017-01-20T18:53:34 |
 | bdcb930d-df41-11e6-b097-5254006ed58e | node-6.domain.tld-SOCKET_0_CHANNEL_any_DIMM_any-uncorrected_memory_errors        | mcelog.errors    | gauge | 0.0          | None    | 2017-01-20T18:53:33 |

