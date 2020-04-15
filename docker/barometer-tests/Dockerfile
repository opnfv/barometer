FROM opnfv/functest-core:hunter

ARG BRANCH=master
ARG OPNFV_BRANCH=stable/hunter
ARG OPENSTACK_TAG=stable/rocky

RUN apk --no-cache add --virtual .build-deps --update \
        python-dev build-base linux-headers libffi-dev \
        openssl-dev libjpeg-turbo-dev && \
    wget -q -O- https://opendev.org/openstack/requirements/raw/branch/$OPENSTACK_TAG/upper-constraints.txt > upper-constraints.txt && \
    wget -q -O- https://git.opnfv.org/functest/plain/upper-constraints.txt?h=$OPNFV_BRANCH > upper-constraints.opnfv.txt && \
    sed -i -E /#egg=baro_tests/d upper-constraints.opnfv.txt && \
    pip install --no-cache-dir --src /src -cupper-constraints.txt -cupper-constraints.opnfv.txt \
        git+https://gerrit.opnfv.org/gerrit/barometer@$BRANCH#egg=baro_tests && \
    rm -r upper-constraints.txt upper-constraints.opnfv.txt && \
    apk del .build-deps
COPY testcases.yaml /usr/lib/python2.7/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
