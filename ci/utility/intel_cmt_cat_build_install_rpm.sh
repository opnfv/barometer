#!/bin/bash
# Copyright 2017 Intel Corporation
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

VERSION="v1.0.1"

bash $DIR/check_git_repo.sh $CMTCAT_DIR $CMTCAT_REPO
if [[ $? != 0 ]]
then
	rm -rf $CMTCAT_DIR
	git clone --branch $CMTCAT_BRANCH $CMTCAT_REPO $CMTCAT_DIR
else
	cd $CMTCAT_DIR
	git reset HEAD --hard
	git pull
	git checkout -f $CMTCAT_BRANCH
fi

cd $CMTCAT_DIR
make
sudo make install

wget https://github.com/01org/intel-cmt-cat/archive/${VERSION}.tar.gz --directory-prefix=$CMTCAT_DIR

mv $CMTCAT_DIR/${VERSION}.tar.gz $RPM_WORKDIR/SOURCES/

rpmbuild --define "_topdir $RPM_WORKDIR" -bb $CMTCAT_DIR/rpm/intel-cmt-cat.spec

rpm -q intel-cmt-cat
if [ $? -eq 0 ]
then
	echo "*** intel-cmt-cat is already installed"
else
	RPM_NAME=`ls -1 $RPM_DIR | grep -E "cmt-cat-[0-9]"`
	sudo rpm -ivf $RPM_DIR/$RPM_NAME
fi
