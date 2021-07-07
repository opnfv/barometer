# This script is used by the barometer-daily CI job in gitlab.
# It builds and packages collectd as an RPM
# After this script is run, the barometer-daily job runs the
# barometer-upload-artifact.sh script.
set -x

OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
OPNFV_ARTIFACT_URL="$GS_URL/$OPNFV_ARTIFACT_VERSION/"

# log info to console
echo "Starting the build of Barometer RPMs"
echo "------------------------------------"
echo

./install_dependencies.sh
./build_rpm.sh
cp utility/rpms_list $WORKSPACE

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_ARTIFACT_URL=$OPNFV_ARTIFACT_URL"
) > $WORKSPACE/opnfv.properties

