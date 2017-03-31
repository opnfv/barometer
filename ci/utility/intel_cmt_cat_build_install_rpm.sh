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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/package-list.sh

VERSION="v0.1.5-1"

git clone https://github.com/01org/intel-cmt-cat.git $CMTCAT_DIR
cd $CMTCAT_DIR
make
sudo make install

wget https://github.com/01org/intel-cmt-cat/archive/${VERSION}.tar.gz

mv ${VERSION}.tar.gz ~/rpmbuild/SOURCES/

rpmbuild -bb ./rpm/intel-cmt-cat.spec

rpm -q intel-cmt-cat
if [ $? -eq 0 ]
then
	echo "*** intel-cmt-cat is allready installed"
else
	RPM_NAME=`ls -1 $RPM_DIR | grep -E "cmt-cat-[0-9]"`
	rpm -ivf $RPM_DIR/$RPM_NAME
fi
