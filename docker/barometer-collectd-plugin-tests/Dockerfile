FROM opnfv/barometer-collectd-tests-base:latest

ENV COLLECTD_FLAVOR experimental
ENV WITH_DPDK y
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins
ENV tests /src/barometer/docker/barometer-collectd-plugin-tests

COPY docker/barometer-collectd-plugin-tests/collectd_apply_pull_request.sh \
     ${repos_dir}/barometer/src/collectd/

WORKDIR ${repos_dir}/barometer/src/collectd/
RUN chmod +x collectd_apply_pull_request.sh
CMD ["/.collectd_apply_pull_request.sh 3045"]

WORKDIR ${openstack_plugins}
RUN make && \
        pip3 install --upgrade pip && \
        pip3 install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt && \
        pip3 install -r ${tests}/test_cases/requirements.txt


COPY docker/barometer-collectd-plugin-tests/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]

WORKDIR tests
#RUN python3 ${tests}/run_tests.py
