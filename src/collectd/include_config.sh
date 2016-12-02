#!/bin/bash
COLLECTD_CONF_FILE=/opt/collectd/etc/collectd.conf
INCLUDE_CONF="<Include \"/opt/collectd/etc/collectd.conf.d\">"

function write_include {
    echo $INCLUDE_CONF | sudo tee -a $COLLECTD_CONF_FILE;
    echo "  Filter \"*.conf\"" | sudo tee -a $COLLECTD_CONF_FILE;
    echo -e "</Include>" | sudo tee -a /opt/collectd/etc/collectd.conf
}

grep -qe '<Include "/opt/collectd/etc/collectd.conf.d">' $COLLECTD_CONF_FILE; [ $? -ne 0 ] && write_include

