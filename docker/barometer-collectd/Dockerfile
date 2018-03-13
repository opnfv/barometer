# build artifacts
FROM centos:7 as collectd_artifacts
RUN yum update -y && \
        yum install -y which sudo git make && \
        yum clean all && \
        git config --global http.sslVerify false

ENV DOCKER y
ENV repos_dir /src
ENV WORKSPACE /tmp
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR ${repos_dir}/barometer/ci
RUN sh ./install_dependencies.sh
RUN sh ./build_rpm.sh

# copy artifacts and create resulting container image
FROM centos:7

WORKDIR /var/cache/yum/local
COPY --from=collectd_artifacts /tmp/rpmbuild/RPMS/x86_64/*.rpm ./

RUN yum -y install epel-release && yum -y install net-snmp-libs *.rpm && \
        yum clean all && rm -rf /var/cache/yum && \
        useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /
COPY run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
