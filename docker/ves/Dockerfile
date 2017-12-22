FROM centos:7
RUN yum update -y && \
    yum install -y epel-release \
                   git \
                   nc

RUN yum install -y python-pip
RUN pip install pyyaml \
                kafka-python

ENV repos_dir /src

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR barometer/3rd_party/collectd-ves-app/ves_app
COPY start_ves_app.sh .
RUN chmod 755 start_ves_app.sh
ENTRYPOINT ["./start_ves_app.sh"]
CMD ["native.yaml"]
