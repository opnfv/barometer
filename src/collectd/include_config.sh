#!/bin/bash
# Copyright 2017 OPNFV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
