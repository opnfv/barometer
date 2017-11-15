#!/bin/bash
COLLECTD_CONF_FILE=/opt/collectd/etc/collectd.conf
COLLECTD_CONF_DIR=/opt/collectd/etc/collectd.conf.d
INCLUDE_CONF="<Include \"/opt/collectd/etc/collectd.conf.d\">"
CURR_DIR=`pwd`
HOSTNAME=`hostname`
SAMPLE_CONF_DIR=$CURR_DIR/collectd_sample_configs/*

function write_include {
    echo "Hostname \"$HOSTNAME\"" | sudo tee -a $COLLECTD_CONF_FILE;
    echo $INCLUDE_CONF | sudo tee -a $COLLECTD_CONF_FILE;
    echo "  Filter \"*.conf\"" | sudo tee -a $COLLECTD_CONF_FILE;
    echo -e "</Include>" | sudo tee -a $COLLECTD_CONF_FILE;
}

grep -qe '<Include "/opt/collectd/etc/collectd.conf.d">' $COLLECTD_CONF_FILE; [ $? -ne 0 ] && write_include

`mkdir -p $COLLECTD_CONF_DIR`

for F in $SAMPLE_CONF_DIR; do
   FILE=$(basename $F)
   [ -f $COLLECTD_CONF_DIR/$FILE ] && echo "File $COLLECTD_CONF_DIR/$FILE exists" || cp $F $COLLECTD_CONF_DIR
done
