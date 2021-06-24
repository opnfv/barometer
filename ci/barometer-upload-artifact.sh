#!/bin/bash
set -o nounset
set -o pipefail

RPM_LIST=$WORKSPACE/rpms_list
RPM_WORKDIR=$WORKSPACE/rpmbuild
RPM_DIR=$RPM_WORKDIR/RPMS/x86_64/
cd $WORKSPACE/

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

# Check if all the appropriate RPMs were generated
echo "Checking if all the Barometer RPMs were created"
echo "-----------------------------------------------"
echo

if [ -d $RPM_DIR ]
then
    ls $RPM_DIR > list_of_gen_pack
else
    echo "Can't access folder $RPM_DIR with rpm packages"
    echo "Barometer nightly build FAILED"
    exit 1
fi

for PACKAGENAME in `cat $RPM_LIST`
do
        if ! grep -q $PACKAGENAME list_of_gen_pack
        then
                echo "$PACKAGENAME is missing"
                echo "Barometer nightly build FAILED"
                exit 2
        fi
done

#remove the file you no longer need.
rm list_of_gen_pack

echo "Uploading the barometer RPMs to artifacts.opnfv.org"
echo "---------------------------------------------------"
echo

gsutil -m cp -r $RPM_DIR/* gs://$OPNFV_ARTIFACT_URL > $WORKSPACE/gsutil.log 2>&1

# Check if the RPMs were pushed
gsutil ls gs://$OPNFV_ARTIFACT_URL > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "Problem while uploading barometer RPMs to gs://$OPNFV_ARTIFACT_URL!"
  echo "Check log $WORKSPACE/gsutil.log on the appropriate build server"
  exit 1
else
  # upload property files only if build is successful
  gsutil cp $WORKSPACE/opnfv.properties gs://$OPNFV_ARTIFACT_URL/opnfv.properties > gsutil.properties.log 2>&1
  gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1
fi

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$OPNFV_ARTIFACT_URL/*.rpm > /dev/null 2>&1

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$OPNFV_ARTIFACT_URL/opnfv.properties > /dev/null 2>&1

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "Artifact is available at $OPNFV_ARTIFACT_URL"

#cleanup the RPM repo from the build machine.
rm -rf $RPM_WORKDIR
