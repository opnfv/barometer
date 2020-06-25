FROM opnfv/barometer-collectd-tests-base:latest

# use environemnt variables to get PRs
ARG PR
ENV PR ${PR:-3292}
RUN echo "Building for :" ${PR}

ENV COLLECTD_FLAVOR tests
ENV WITH_DPDK y
ENV openstack_plugins /src/barometer/src/collectd-openstack-plugins
ENV tests /src/barometer/docker/barometer-collectd-plugin-tests

COPY docker/barometer-collectd-plugin-tests/collectd_apply_pull_request.sh \
     ${repos_dir}/barometer/src/collectd/

WORKDIR ${repos_dir}/barometer/src/collectd/
RUN chmod +x collectd_apply_pull_request.sh
CMD ["/.collectd_apply_pull_request.sh ${PR}"]

#Download AER inject module & Download and build aer-inject tool:
WORKDIR /logparser_testutils/
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/l/linux/linux_4.4.0.orig.tar.gz
RUN tar xzvf linux_4.4.0.orig.tar.gz
RUN cd linux-4.4/drivers/pci/pcie/aer/
RUN yum -y install kernel-devel
#TODO:
# change this to a query
RUN CONFIG_PCIEAER_INJECT=m make -C /usr/src/kernels/3.10.0-1127.13.1.el7.x86_64/build M=$PWD modules
RUN insmod aer_inject.ko


WORKDIR /test_utils/logparser_testutils/
RUN yum install bison flex
RUN git clone https://kernel.googlesource.com/pub/scm/linux/kernel/git/gong.chen/aer-inject
RUN cd aer-inject
RUN make

WORKDIR ${openstack_plugins}
RUN make && \
        pip3 install --upgrade pip && \
        pip3 install -r ${openstack_plugins}/collectd-openstack-plugins/requirements.txt


COPY docker/barometer-collectd-plugin-tests/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh


COPY docker/barometer-collectd-plugin-tests/commands.sh /scripts/commands.sh
RUN ["chmod", "+x", "/scripts/commands.sh"]
ENTRYPOINT ["/scripts/commands.sh"]
