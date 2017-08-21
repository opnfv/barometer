#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/package-list.sh

if [ -d $RPM_WORKDIR/RPMS/x86_64 ]
then
    ls $RPM_WORKDIR/RPMS/x86_64 > list_of_gen_pack
else
    echo "Can't access folder $RPM_WORKDIR with rpm packages"
    exit 1
fi

for PACKAGENAME in `cat $DIR/rpms_list`
do
        if ! grep -q $PACKAGENAME list_of_gen_pack
        then
                echo "$PACKAGENAME is missing"
                exit 2
        fi
done
