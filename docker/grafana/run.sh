#!/bin/bash -e
# Copyright 2014-2016 Torkel Ödegaard, Raintank Inc.
# Modifications Copyright 2017 OPNFV
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

: "${GF_PATHS_CONFIG:=/etc/grafana/grafana.ini}"
: "${GF_PATHS_DATA:=/var/lib/grafana}"
: "${GF_PATHS_LOGS:=/var/log/grafana}"
: "${GF_PATHS_PLUGINS:=/var/lib/grafana/plugins}"

chown -R grafana:grafana "$GF_PATHS_DATA" "$GF_PATHS_LOGS"
chown -R grafana:grafana /etc/grafana


if [ ! -z ${GF_AWS_PROFILES+x} ]; then
    mkdir -p ~grafana/.aws/
    touch ~grafana/.aws/credentials

    for profile in ${GF_AWS_PROFILES}; do
        access_key_varname="GF_AWS_${profile}_ACCESS_KEY_ID"
        secret_key_varname="GF_AWS_${profile}_SECRET_ACCESS_KEY"
        region_varname="GF_AWS_${profile}_REGION"

        if [ ! -z "${!access_key_varname}" -a ! -z "${!secret_key_varname}" ]; then
            echo "[${profile}]" >> ~grafana/.aws/credentials
            echo "aws_access_key_id = ${!access_key_varname}" >> ~grafana/.aws/credentials
            echo "aws_secret_access_key = ${!secret_key_varname}" >> ~grafana/.aws/credentials
            if [ ! -z "${!region_varname}" ]; then
                echo "region = ${!region_varname}" >> ~grafana/.aws/credentials
            fi
        fi
    done

    chown grafana:grafana -R ~grafana/.aws
    chmod 600 ~grafana/.aws/credentials
fi

if [ ! -z "${GF_INSTALL_PLUGINS}" ]; then
  OLDIFS=$IFS
  IFS=','
  for plugin in ${GF_INSTALL_PLUGINS}; do
    IFS=$OLDIFS
    gosu grafana grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ${plugin}
  done
fi

/bin/bash ./configure_grafana.sh &

exec gosu grafana /usr/sbin/grafana-server      \
  --homepath=/usr/share/grafana                 \
  --config="$GF_PATHS_CONFIG"                   \
  cfg:default.log.mode="console"                \
  cfg:default.paths.data="$GF_PATHS_DATA"       \
  cfg:default.paths.logs="$GF_PATHS_LOGS"       \
  cfg:default.paths.plugins="$GF_PATHS_PLUGINS" \
  "$@"



