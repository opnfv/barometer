#! /bin/bash
# Copyright 2019-2021 Intel Corporation, Anuket and others.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# This files contains list of pull requests to be applied on top
# of main branch before building collectd included in docker
# collectd-experimental container

# Use this script with a COLLECTD_PULL_REQUESTS variable defined
# for example:
# COLLECTD_PULL_REQUESTS="3027,3028" ./collectd_apply_pull_request.sh

if [ -z "$COLLECTD_PULL_REQUESTS" ];
then
	echo "COLLECTD_PULL_REQUESTS is unset, exiting"
	exit
fi

IFS=', ' read -a PULL_REQUESTS <<< "$COLLECTD_PULL_REQUESTS"

# during rebasing/merging git requires email & name to be set
git config user.email "barometer-experimental@container"
git config user.name "BarometerExperimental"

for PR_ID in "${PULL_REQUESTS[@]}"
do
    echo "Applying pull request $PR_ID"
    git pull --rebase origin pull/$PR_ID/head
done
