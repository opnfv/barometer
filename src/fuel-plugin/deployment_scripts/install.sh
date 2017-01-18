#!/bin/bash
set -eux

INSTALL_HOME=/opt/collectd-ceilometer

HOST=$1
OS_AUTH_URL=$2
OS_USERNAME=$3
OS_PASSWORD=$4
enable_mcelog=$5
enable_intel_rdt=$6
enable_hugepages=$7
enable_ovs_events=$8

CEILOMETER_URL_TYPE=${CEILOMETER_URL_TYPE:-internalURL}
CEILOMETER_TIMEOUT=${CEILOMETER_TIMEOUT:-1000}

MCELOG_SOCKET="socket-path = /var/run/mcelog-client"
MCELOG_CONF="/etc/mcelog/mcelog.conf"

rm -rf $INSTALL_HOME; mkdir -p $INSTALL_HOME
cd $INSTALL_HOME
curl http://$HOST:8080/plugins/fuel-plugin-collectd-ceilometer-1.0/repositories/ubuntu/collectd-ceilometer.tgz | tar xzvf -

cat << EOF > /etc/ld.so.conf.d/pqos.conf
$INSTALL_HOME/lib
EOF
ldconfig
modprobe msr

apt-get install -y --allow-unauthenticated collectd python-dev libpython2.7 mcelog

echo $MCELOG_SOCKET | sudo tee -a $MCELOG_CONF;

cat << EOF > /etc/collectd/collectd.conf.d/collectd-ceilometer-plugin.conf
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
    ModulePath "$INSTALL_HOME/collectd-ceilometer-plugin"
    LogTraces true
    Interactive false
    Import "collectd_ceilometer.plugin"

    <Module "collectd_ceilometer.plugin">

        # Verbosity 1|0
        #VERBOSE 0

        # Batch size
        BATCH_SIZE 3

        # Service endpoint addresses
        OS_AUTH_URL "$OS_AUTH_URL"

        # Ceilometer address
        #CEILOMETER_ENDPOINT
        CEILOMETER_URL_TYPE "$CEILOMETER_URL_TYPE"

        # Ceilometer timeout in ms
        CEILOMETER_TIMEOUT "$CEILOMETER_TIMEOUT"

        # # Ceilometer user creds
        OS_USERNAME "$OS_USERNAME"
        OS_PASSWORD "$OS_PASSWORD"
        OS_TENANT_NAME "services"

    </Module>
</Plugin>
EOF

if [ $enable_intel_rdt = 'true' ]
then
    cat << EOF > /etc/collectd/collectd.conf.d/intel-rdt.conf
<LoadPlugin intel_rdt>
  Interval 1
</LoadPlugin>

<Plugin "intel_rdt">
  Cores ""
</Plugin>
EOF
fi

if [ $enable_hugepages = 'true' ]
then
    cat << EOF > /etc/collectd/collectd.conf.d/hugepages.conf
LoadPlugin hugepages

<Plugin hugepages>
    ReportPerNodeHP  true
    ReportRootHP     true
    ValuesPages      true
    ValuesBytes      false
    ValuesPercentage false
</Plugin>
EOF
fi

if [ $enable_mcelog = 'true' ]
then
cat << EOF > /etc/collectd/collectd.conf.d/mcelog.conf
<LoadPlugin mcelog>
  Interval 1
</LoadPlugin>
<Plugin "mcelog">
   McelogClientSocket "/var/run/mcelog-client"
</Plugin>
EOF
fi

service collectd restart
