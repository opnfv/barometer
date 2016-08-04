#!/bin/bash
set -eux

INSTALL_HOME=/opt/collectd-ceilometer

HOST=$1
OS_AUTH_URL=$2
OS_USERNAME=$3
OS_PASSWORD=$4

CEILOMETER_URL_TYPE=${CEILOMETER_URL_TYPE:-internalURL}
CEILOMETER_TIMEOUT=${CEILOMETER_TIMEOUT:-1000}

apt-get install -y collectd
service collectd stop

rm -rf $INSTALL_HOME; mkdir -p $INSTALL_HOME
cd $INSTALL_HOME
curl http://$HOST:8080/plugins/fuel-plugin-collectd-ceilometer-0.9/repositories/ubuntu/collectd-ceilometer.tgz | tar xzvf -

cat << EOF > /etc/collectd/collectd.conf.d/collectd-ceilometer-plugin.conf
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
    ModulePath "$INSTALL_HOME"
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

#fixme: sleep 3 minutes to wait for ceilometer api ready in controller node
sleep 180

service collectd start
