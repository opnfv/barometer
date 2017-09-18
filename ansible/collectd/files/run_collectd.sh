#!/bin/bash
modprobe msr
/opt/collectd/sbin/collectd -f
