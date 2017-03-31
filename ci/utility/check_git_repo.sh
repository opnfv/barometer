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

TARGET_DIR=$1
REPO=$2

if [[ ! $1 ]]
then
	echo "Test if target dir contains the given git repository"
	echo "Usage: $0 <TARGET_DIR> <REPO_ADDRESS>"
	exit 254
fi

cd $TARGET_DIR
if [[ $? != 0 ]]
then
	echo "Directory is not existing"
	exit 1
fi

git status &>/dev/null
if [[ $? != 0 ]]
then
	echo "Not a git repo"
	exit 2
else
	REMOTE=`git remote -vv | sed -e "2d" -r -e 's|^\S+\s(\S+)\s\S+$|\1|'`
	if [[ "$REMOTE" == "$REPO" ]]
	then
		echo "YEP"
		exit 0
	else
		echo "Wrong repo"
		exit 3
	fi
fi

exit 255
