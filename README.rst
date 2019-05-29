Barometer
---------
.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

::

    Note: this repository provides a demo implementation. It is not intended
    for unmodified use in production. It has not been tested for production.



The ability to monitor the Network Function Virtualization Infrastructure
(NFVI) where VNFs are in operation will be a key part of Service Assurance
within an NFV environment, in order to enforce SLAs or to detect violations,
faults or degradation in the performance of NFVI resources so that events
and relevant metrics are reported to higher level fault management systems.
If fixed function appliances are going to be replaced by virtualized
appliances the service levels, manageability and service assurance needs
to remain consistent or improve on what is available today.

As such, the NFVI needs to support the ability to monitor:

#. Traffic monitoring and performance monitoring of the components that
   provide networking functionality to the VNF, including: physical
   interfaces, virtual switch interfaces and flows, as well as the
   virtual interfaces themselves and their status, etc.
#. Platform monitoring including: CPU, memory, load, cache, thermals, fan
   speeds, voltages and machine check exceptions, etc.


All of the statistics and events gathered must be collected in-service and
must be capable of being reported by standard Telco mechanisms (e.g. SNMP,
REST), for potential enforcement or correction actions. In addition, this
information could be fed to analytics systems to enable failure prediction,
and can also be used for intelligent workload placement.


