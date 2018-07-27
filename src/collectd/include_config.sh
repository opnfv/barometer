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

# Config file options are changing between releases so we have to store both
# configurations variants and choose correct one for target collectd version

if [ -z "$1" ]; then
    echo "Error! Please sample configs variant name as a param!"\
         "(name of directory with sample-configs)"
    echo "Usage:"
    echo "$0 SAMPLE_CONFIGS_VARIANT_NAME"
    echo "e.g. $0 'collectd_sample_configs'"
    exit 1
fi

SAMPLE_CONF_VARIANT="$1"
COLLECTD_CONF_FILE=/opt/collectd/etc/collectd.conf
COLLECTD_CONF_DIR=/opt/collectd/etc/collectd.conf.d
INCLUDE_CONF="<Include \"/opt/collectd/etc/collectd.conf.d\">"
CURR_DIR=`pwd`
HOSTNAME=`hostname`
SAMPLE_CONF_DIR=$CURR_DIR/$SAMPLE_CONF_VARIANT

if [ ! -d "$SAMPLE_CONF_DIR" ]; then
    echo "$SAMPLE_CONF_DIR does not exits!"\
         "Probably passed bad variant name as a param: $SAMPLE_CONF_VARIANT"
    exit 1
fi

function write_include {
    echo "Hostname \"$HOSTNAME\"" | sudo tee -a $COLLECTD_CONF_FILE;
    echo $INCLUDE_CONF | sudo tee -a $COLLECTD_CONF_FILE;
    echo "  Filter \"*.conf\"" | sudo tee -a $COLLECTD_CONF_FILE;
    echo -e "</Include>" | sudo tee -a $COLLECTD_CONF_FILE;
}

grep -qe '<Include "/opt/collectd/etc/collectd.conf.d">' $COLLECTD_CONF_FILE; [ $? -ne 0 ] && write_include

`mkdir -p $COLLECTD_CONF_DIR`

SAMPLE_CONF_FILES=$SAMPLE_CONF_DIR/*
for F in $SAMPLE_CONF_FILES; do
   FILE=$(basename $F)
   [ -f $COLLECTD_CONF_DIR/$FILE ] && echo "File $COLLECTD_CONF_DIR/$FILE exists" || cp $F $COLLECTD_CONF_DIR
done
