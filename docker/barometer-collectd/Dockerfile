# build artifacts
FROM centos:7 as collectd_artifacts
RUN yum update -y && \
        yum install -y which sudo git && \
        yum clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV repos_dir /src
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh
WORKDIR /usr/lib64
RUN ln -s ../lib/libpqos.so.1 .

# copy artifacts and create resulting container image
FROM centos:7

WORKDIR /opt/
COPY --from=collectd_artifacts /opt/collectd/ collectd/

WORKDIR /usr/lib/
COPY --from=collectd_artifacts /usr/lib/ .

WORKDIR /usr/lib64/
COPY --from=collectd_artifacts /usr/lib64/ .

RUN yum -y install net-snmp-libs && yum clean all && rm -rf /var/cache/yum && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /usr/share/snmp/mibs/
COPY --from=collectd_artifacts /src/barometer/mibs/ .

WORKDIR /
COPY run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
