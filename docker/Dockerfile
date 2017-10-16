FROM centos:7
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}
RUN yum update -y
RUN yum install -y which sudo
ENV DOCKER y
COPY systems /systems
COPY src /src
COPY 3rd_party /3rd_party
COPY mibs /mibs

WORKDIR /systems
RUN sh ./build_base_machine.sh
RUN useradd -ms /bin/bash collectd_exec
RUN echo "collectd_exec ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
WORKDIR /src

COPY docker/run_collectd.sh /run_collectd.sh
RUN chmod +x /run_collectd.sh
