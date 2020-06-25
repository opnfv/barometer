FROM centos:7
RUN yum update -y && \
        yum install -y which sudo git && \
        yum clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV COLLECTD_FLAVOR master
ENV WITH_DPDK y
ENV repos_dir /src
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins
ENV tests /src/barometer/docker/barometer-collectd-plugin-tests


WORKDIR ${repos_dir}
RUN mkdir -p ${repos_dir}/barometer
COPY . ${repos_dir}/barometer
COPY docker/barometer-collectd-plugin-tests/collectd_apply_pull_request.sh \
     ${repos_dir}/barometer/src/collectd/


WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers


WORKDIR ${openstack_plugins}
RUN make && \
        pip3 install --upgrade pip && \
        pip3 install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt && \
        pip3 install -r ${tests}/test_cases/requirements.txt


COPY docker/barometer-collectd-plugin-tests/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]

#here we will execute the python file run_tests.py
RUN python3 ${tests}/run_tests.py
