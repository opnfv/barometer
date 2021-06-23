#!/bin/bash
# Copyright 2017-21 Anuket, Intel Corporation and others
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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/utility/package-list.sh

# Reuse build_base_machine.sh for this distro, to install the required packages
# Detect OS name and version from systemd based os-release file
. /etc/os-release
distro_dir="$DIR/../systems/$ID/$VERSION_ID"

# build base system using OS specific scripts
if [ -d "$distro_dir" ] && [ -e "$distro_dir/build_base_machine.sh" ]; then
    sudo $distro_dir/build_base_machine.sh || ( echo "$distro_dir/build_base_machine.sh failed" && exit 1 )
else
    "$distro_dir is not supported"
    exit 1
fi

# For RPM build
mkdir -p $RPM_WORKDIR/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
