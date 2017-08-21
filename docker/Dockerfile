FROM centos:7

RUN yum update -y
RUN yum install -y git which sudo wget cmake yajl-devel gcc-c++ autoconf \
    automake flex bison libtool libxml2-devel libvirt libvirt-devel \
    pkg-config make yum-utils epel-release

#jevents (for intel pmu stats)
WORKDIR /
RUN git clone https://github.com/andikleen/pmu-tools
WORKDIR /pmu-tools/jevents
#change Makefile (CFLAGS add -fPIC directive)
RUN sed -i 's/CFLAGS := -g -Wall -O2 -Wno-unused-result/CFLAGS := -g -Wall -O2 -Wno-unused-result -fPIC/' Makefile
RUN make
RUN make install

WORKDIR /
RUN git clone http://github.com/01org/intel-cmt-cat
WORKDIR /intel-cmt-cat
RUN make
RUN make install PREFIX=/usr

WORKDIR /
RUN git clone https://github.com/collectd/collectd
WORKDIR /collectd
RUN ./build.sh
RUN ./configure --with-libjevents=/usr/local
#RUN ./configure --with-libjevents=/usr/local --enable-debug
RUN make all install

COPY collectd.conf /opt/collectd/etc/collectd.conf
COPY collectd.d/csv.conf /opt/collectd/etc/collectd.d/
