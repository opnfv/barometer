FROM centos:7
RUN yum update -y && yum install -y epel-release \
                   wget \
                   https://archive.cloudera.com/cdh5/one-click-install/redhat/7/x86_64/cloudera-cdh-5-0.x86_64.rpm \
                   java-1.7.0-openjdk
RUN yum install -y python-pip \
                   zookeeper

RUN pip install kafka-python

ENV repos_dir /src
WORKDIR ${repos_dir}

RUN wget "https://archive.apache.org/dist/kafka/1.0.0/kafka_2.11-1.0.0.tgz"
RUN tar -xvzf kafka_2.11-1.0.0.tgz
RUN sed -i -- 's/#delete.topic.enable=true/delete.topic.enable=true/' kafka_2.11-1.0.0/config/server.properties
RUN /usr/lib/zookeeper/bin/zkServer-initialize.sh
COPY start_kafka.sh ${repos_dir}
RUN chmod 755 start_kafka.sh
ENTRYPOINT ["/src/start_kafka.sh"]
