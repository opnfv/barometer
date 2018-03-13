# --- build artifacts
FROM centos:7 as collectd_artifacts
RUN yum update -y && \
        yum install -y which sudo && yum clean all

ENV DOCKER y
ENV repos_dir /src
ENV WORKSPACE /workspace
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

# copy in current working source and build RPMs
WORKDIR ${repos_dir}
COPY ./ ./barometer
WORKDIR ${repos_dir}/barometer/ci
RUN sh ./install_dependencies.sh && sh ./build_rpm.sh

# obtain openstack collect plugins
WORKDIR ${openstack_plugins}
RUN make


# --- copy artifacts and create resulting container image
FROM centos:7

ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins

# collectd openstack plugins
WORKDIR ${openstack_plugins}
COPY --from=collectd_artifacts ${openstack_plugins}/collectd-openstack-plugins/ ./

# barometer collectd RPMs
WORKDIR /var/cache/yum/local
COPY --from=collectd_artifacts /workspace/rpmbuild/RPMS/x86_64/*.rpm ./

# install dependencies and collectd
RUN yum -y install epel-release && yum -y install net-snmp-libs python-pip *.rpm && \
        yum clean all && rm -rf /var/cache/yum

# setup sudo and install openstack collectd polugins
WORKDIR /
RUN useradd -ms /bin/bash collectd_exec && \
        echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
        pip install -r ${openstack_plugins}/requirements.txt

# copy in entrypoint script
COPY ./docker/barometer-collectd/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
