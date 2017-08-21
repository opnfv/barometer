FROM centos:7

RUN yum update -y
RUN yum install -y which sudo
ENV DOCKER y
COPY systems /systems
COPY src /src
COPY 3rd_party /3rd_party

WORKDIR /systems
RUN sh ./build_base_machine.sh

WORKDIR /src

COPY docker/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh
