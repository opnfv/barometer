# Copyright 2017-2019 Intel Corporation and OPNFV. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM centos:7
RUN yum update -y && yum install -y epel-release \
                   wget \
                   https://archive.cloudera.com/cdh5/one-click-install/redhat/7/x86_64/cloudera-cdh-5-0.x86_64.rpm \
                   java-1.7.0-openjdk
RUN yum install -y python-pip

RUN pip install kafka-python

ENV repos_dir /src
WORKDIR ${repos_dir}
EXPOSE 9092

RUN wget "https://archive.apache.org/dist/kafka/1.0.0/kafka_2.11-1.0.0.tgz"
RUN tar -xzf kafka_2.11-1.0.0.tgz
RUN sed -i -- 's/#delete.topic.enable=true/delete.topic.enable=true/' kafka_2.11-1.0.0/config/server.properties

COPY start_kafka.sh .
RUN chmod 755 start_kafka.sh
ENTRYPOINT ["/src/start_kafka.sh"]
