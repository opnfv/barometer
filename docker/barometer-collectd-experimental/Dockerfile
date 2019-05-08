FROM centos:7
RUN yum update -y && \
        yum install -y which sudo git && \
        yum clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV COLLECTD_FLAVOR experimental
ENV WITH_DPDK y
ENV repos_dir /src
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

WORKDIR ${repos_dir}
RUN mkdir -p ${repos_dir}/barometer
COPY . ${repos_dir}/barometer
COPY docker/barometer-collectd-experimental/collectd_apply_pull_request.sh \
     ${repos_dir}/barometer/src/collectd/

# copying additional experimental configs on top of configs for 'master'
# branch release
COPY docker/barometer-collectd-experimental/experimental-configs/* \
     ${repos_dir}/barometer/src/collectd/collectd_sample_configs-master/

WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR ${openstack_plugins}
RUN make && \
        pip install --upgrade pip && \
        pip install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt

COPY docker/barometer-collectd-experimental/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
