FROM influxdb:1.3.7

RUN wget https://raw.githubusercontent.com/collectd/collectd/collectd-5.10/src/types.db -O /types.db
COPY ./influxdb.conf /etc/influxdb/influxdb.conf
