#!/bin/sh
# Copyright (C) 2017-2019 Intel Corporation and OPNFV. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/package-list.sh

if [ -d $RPM_WORKDIR/RPMS/x86_64 ]
then
    ls $RPM_WORKDIR/RPMS/x86_64 > list_of_gen_pack
else
    echo "Can't access folder $RPM_WORKDIR with rpm packages"
    exit 1
fi

for PACKAGENAME in `grep -v ^# $DIR/rpms_list`
do
        if ! grep -q $PACKAGENAME list_of_gen_pack
        then
                echo "$PACKAGENAME is missing"
                exit 2
        fi
done
