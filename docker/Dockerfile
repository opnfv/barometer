FROM centos:7

RUN yum update -y
RUN yum install -y which sudo

COPY systems /systems
RUN sh /systems/centos/7/build_base_machine.sh

WORKDIR /
RUN git clone https://github.com/andikleen/pmu-tools
WORKDIR /pmu-tools/jevents
RUN sed -i 's/CFLAGS := -g -Wall -O2 -Wno-unused-result/CFLAGS := -g -Wall -O2 -Wno-unused-result -fPIC/' Makefile
RUN make
RUN make install

WORKDIR /
RUN git clone http://github.com/01org/intel-cmt-cat
WORKDIR /intel-cmt-cat
RUN make
RUN make install PREFIX=/usr

COPY src /src
WORKDIR /src
RUN make MSR_DISABLED=1 DPDK_DISABLED=1 DOCKER=1
RUN make install MSR_DISABLED=1 DPDK_DISABLED=1 DOCKER=1

RUN echo '<Include "/opt/collectd/etc/collectd.d">' >> /opt/collectd/etc/collectd.conf
RUN echo '   Filter "*.conf"' >> /opt/collectd/etc/collectd.conf
RUN echo '</Include>' >> /opt/collectd/etc/collectd.conf

COPY docker/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh
