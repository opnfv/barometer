#!/bin/bash
# Copyright 2017-2019 Intel Corporation and OPNFV. All rights reserved.
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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/package-list.sh

VERSION="VERSION_NOT_SET"

cd $COLLECTD_DIR
VERSION=$( $COLLECTD_DIR/version-gen.sh )
$COLLECTD_DIR/clean.sh
$COLLECTD_DIR/build.sh
$COLLECTD_DIR/configure
sed     --regexp-extended \
        --in-place=".bak" \
        --expression="s/^CapabilityBoundingSet=/CapabilityBoundingSet=CAP_SETUID CAP_SETGID CAP_SYS_RAWIO/g" \
        $COLLECTD_DIR/contrib/systemd.collectd.service
make dist

cp $COLLECTD_DIR/collectd-$VERSION.tar.bz2 $RPM_WORKDIR/SOURCES/

git apply $DIR/collectd.spec.patch

sed	--regexp-extended \
	--in-place=".bak" \
	--expression="s/Version:\s+\S+$/Version:	$VERSION/g" \
	$COLLECTD_DIR/contrib/redhat/collectd.spec

rpmbuild --define "_topdir $RPM_WORKDIR" --define "without_intel_rdt 1" -bb $COLLECTD_DIR/contrib/redhat/collectd.spec

