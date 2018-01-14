FROM grafana/grafana:4.6.3

ENV grafana_folder /opt/grafana
RUN mkdir -p ${grafana_folder}/dashboards/

COPY ./configure_grafana.sh ${grafana_folder}
COPY ./run.sh /
COPY ./dashboards/ ${grafana_folder}/dashboards/

WORKDIR $grafana_folder
RUN chmod 755 /run.sh configure_grafana.sh
