FROM centos:7
RUN yum update -y && \
    yum install -y epel-release \
                   git \
                   nc

RUN yum install -y python-pip
RUN pip install pyyaml \
                kafka-python

ENV repos_dir /src
ENV ves_dir barometer/3rd_party/collectd-ves-app/ves_app

WORKDIR ${repos_dir}
RUN git clone https://gerrit.opnfv.org/gerrit/barometer
WORKDIR ${ves_dir}
COPY start_ves_app.sh ${ves_dir}/start_ves_app.sh
RUN chmod +x ${ves_dir}/start_ves_app.sh

ENTRYPOINT ["./barometer/3rd_party/collectd-ves-app/ves_app/start_ves_app.sh"]
CMD ["host.yaml"]
