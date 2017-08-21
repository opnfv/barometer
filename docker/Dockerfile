FROM centos:7

RUN yum update -y
RUN yum install -y which sudo
ENV DOCKER y
COPY systems /systems
COPY src /src

WORKDIR /systems
RUN sh ./build_base_machine.sh

WORKDIR /src
RUN echo '<Include "/opt/collectd/etc/collectd.d">' >> /opt/collectd/etc/collectd.conf
RUN echo '   Filter "*.conf"' >> /opt/collectd/etc/collectd.conf
RUN echo '</Include>' >> /opt/collectd/etc/collectd.conf

COPY docker/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh
