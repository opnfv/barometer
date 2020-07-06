#! /bin/bash
##############################################################################
# Copyright (c) 2017 <Company or Individual> and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Space/newline separated list of pull requests IDs
# for example:
# PULL_REQUESTS=(3027 #reimplement delay rate
#                3028 #other PR
#                )


# Parse for the cli inputs for PRs
PULL_REQUESTS=()
i=1;
j=$#;
while [ $i -le $j ]
do
    PULL_REQUESTS[i]="$1"
    i=$((i + 1));
    shift 1;
done

echo ${PULL_REQUESTS[*]}
if [ ${#PULL_REQUESTS[@]} -eq 0 ]; then
       PULL_REQUESTS=(
        3046 #logparser
        #insert another PR ID here
    )
fi

# during rebasing/merging git requires email & name to be set
git config user.email "barometer-experimental@container"
git config user.name "BarometerExperimental"

for PR_ID in "${PULL_REQUESTS[@]}"
do
    echo "Applying pull request $PR_ID"
    git pull --rebase origin pull/$PR_ID/head
done
