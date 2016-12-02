.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) OPNFV, Intel Corporation and others.

collectd
~~~~~~~~
collectd is a daemon which collects system performance statistics periodically
and provides a variety of mechanisms to publish the collected metrics. It
supports more than 90 different input and output plugins. Input plugins retrieve
metrics and publish them to the collectd deamon, while output plugins publish
the data they receive to an end point. collectd also has infrastructure to
support thresholding and notification.

collectd statistics and Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Within collectd notifications and performance data are dispatched in the same
way. There are producer plugins (plugins that create notifications/metrics),
and consumer plugins (plugins that receive notifications/metrics and do
something with them).

Statistics in collectd consist of a value list. A value list includes:

* Values, can be one of:

  * Derive: used for values where a change in the value since it's last been
    read is of interest. Can be used to calculate and store a rate.

  * Counter: similar to derive values, but take the possibility of a counter
    wrap around into consideration.

  * Gauge: used for values that are stored as is.

  * Absolute: used for counters that are reset after reading.

* Value length: the number of values in the data set.

* Time: timestamp at which the value was collected.

* Interval: interval at which to expect a new value.

* Host: used to identify the host.

* Plugin: used to identify the plugin.

* Plugin instance (optional): used to group a set of values together. For e.g.
  values belonging to a DPDK interface.

* Type: unit used to measure a value. In other words used to refer to a data
  set.

* Type instance (optional): used to distinguish between values that have an
  identical type.

* meta data: an opaque data structure that enables the passing of additional
  information about a value list. "Meta data in the global cache can be used to
  store arbitrary information about an identifier" [7].

Host, plugin, plugin instance, type and type instance uniquely identify a
collectd value.

Values lists are often accompanied by data sets that describe the values in more
detail. Data sets consist of:

* A type: a name which uniquely identifies a data set.

* One or more data sources (entries in a data set) which include:

  * The name of the data source. If there is only a single data source this is
    set to "value".

  * The type of the data source, one of: counter, gauge, absolute or derive.

  * A min and a max value.

Types in collectd are defined in types.db. Examples of types in types.db:

.. code-block:: console

    bitrate    value:GAUGE:0:4294967295
    counter    value:COUNTER:U:U
    if_octets  rx:COUNTER:0:4294967295, tx:COUNTER:0:4294967295

In the example above if_octets has two data sources: tx and rx.

Notifications in collectd are generic messages containing:

* An associated severity, which can be one of OKAY, WARNING, and FAILURE.

* A time.

* A Message

* A host.

* A plugin.

* A plugin instance (optional).

* A type.

* A types instance (optional).

* Meta-data.
