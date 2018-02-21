FROM centos:7
RUN yum update -y
RUN yum install -y which sudo
RUN yum install -y git
ENV DOCKER y
ENV repos_dir /src
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins
RUN git config --global http.sslVerify false

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR ${repos_dir}/barometer/systems
RUN sh ./build_base_machine.sh

RUN useradd -ms /bin/bash collectd_exec
RUN echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR ${openstack_plugins}
RUN make
RUN pip install --upgrade pip
RUN pip install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt

COPY run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh

ENTRYPOINT ["/run_collectd.sh"]
