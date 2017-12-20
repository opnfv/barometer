FROM grafana/grafana:latest

COPY ./configure_grafana.sh /
COPY ./run.sh /
COPY ./dashboards/ /var/lib/grafana/dashboards/
RUN chmod 755 run.sh configure_grafana.sh
