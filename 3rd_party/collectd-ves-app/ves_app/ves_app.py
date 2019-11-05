#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import base64
import configparser
import logging
import argparse

from distutils.util import strtobool
from kafka import KafkaConsumer

from .normalizer import Normalizer
from .normalizer import CollectdValue

import urllib.request as url

class VESApp(Normalizer):
    """VES Application"""

    def __init__(self):
        """Application initialization"""
        self._app_config = {
            'Domain': '127.0.0.1',
            'Port': 30000,
            'Path': '',
            'Username': '',
            'Password': '',
            'Topic': '',
            'UseHttps': False,
            'SendEventInterval': 20.0,
            'ApiVersion': 5.1,
            'KafkaPort': 9092,
            'KafkaBroker': 'localhost'
        }

    def send_data(self, event):
        """Send event to VES"""
        server_url = "http{}://{}:{}{}/eventListener/v{}{}".format(
            's' if self._app_config['UseHttps'] else '',
            self._app_config['Domain'], int(self._app_config['Port']),
            '{}'.format('/{}'.format(self._app_config['Path']) if len(
                self._app_config['Path']) > 0 else ''),
            int(self._app_config['ApiVersion']), '{}'.format(
                '/{}'.format(self._app_config['Topic']) if len(
                    self._app_config['Topic']) > 0 else ''))
        logging.info('Vendor Event Listener is at: {}'.format(server_url))
        credentials = base64.b64encode('{}:{}'.format(
            self._app_config['Username'],
            self._app_config['Password']).encode()).decode()
        logging.info('Authentication credentials are: {}'.format(credentials))
        try:
            request = url.Request(server_url)
            request.add_header('Authorization', 'Basic {}'.format(credentials))
            request.add_header('Content-Type', 'application/json')
            event_str = json.dumps(event).encode()
            logging.debug("Sending {} to {}".format(event_str, server_url))
            url.urlopen(request, event_str, timeout=1)
            logging.debug("Sent data to {} successfully".format(server_url))
        except url.HTTPError as e:
            logging.error('Vendor Event Listener exception: {}'.format(e))
        except url.URLError as e:
            logging.error(
                'Vendor Event Listener is is not reachable: {}'.format(e))
        except Exception as e:
            logging.error('Vendor Event Listener error: {}'.format(e))

    def config(self, config):
        """VES option configuration"""
        for key, value in config.items('config'):
            if key in self._app_config:
                try:
                    if type(self._app_config[key]) == int:
                        value = int(value)
                    elif type(self._app_config[key]) == float:
                        value = float(value)
                    elif type(self._app_config[key]) == bool:
                        value = bool(strtobool(value))

                    if isinstance(value, type(self._app_config[key])):
                        self._app_config[key] = value
                    else:
                        logging.error("Type mismatch with %s" % key)
                        sys.exit()
                except ValueError:
                    logging.error("Incorrect value type for %s" % key)
                    sys.exit()
            else:
                logging.error("Incorrect key configuration %s" % key)
                sys.exit()

    def init(self, configfile, schema_file):
        if configfile is not None:
            # read VES configuration file if provided
            config = configparser.ConfigParser()
            config.optionxform = lambda option: option
            config.read(configfile)
            self.config(config)
        # initialize normalizer
        self.initialize(schema_file, self._app_config['SendEventInterval'])

    def run(self):
        """Consumer JSON data from kafka broker"""
        kafka_server = '{}:{}'.format(
            self._app_config.get('KafkaBroker'),
            self._app_config.get('KafkaPort'))
        consumer = KafkaConsumer(
            'collectd', bootstrap_servers=kafka_server,
            auto_offset_reset='latest', enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('ascii')))

        for message in consumer:
            for kafka_data in message.value:
                # {
                #   u'dstypes': [u'derive'],
                #   u'plugin': u'cpu',
                #   u'dsnames': [u'value'],
                #   u'interval': 10.0,
                #   u'host': u'localhost',
                #   u'values': [99.9978996416267],
                #   u'time': 1502114956.244,
                #   u'plugin_instance': u'44',
                #   u'type_instance': u'idle',
                #   u'type': u'cpu'
                # }
                logging.debug('{}:run():data={}'.format(
                    self.__class__.__name__, kafka_data))
                for ds_name in kafka_data['dsnames']:
                    index = kafka_data['dsnames'].index(ds_name)
                    val_hash = CollectdValue.hash_gen(
                        kafka_data['host'], kafka_data['plugin'],
                        kafka_data['plugin_instance'], kafka_data['type'],
                        kafka_data['type_instance'], ds_name)
                    collector = self.get_collector()
                    val = collector.get(val_hash)
                    if val:
                        # update the value
                        val.value = kafka_data['values'][index]
                        val.time = kafka_data['time']
                        del(val)
                    else:
                        # add new value into the collector
                        val = CollectdValue()
                        val.host = kafka_data['host']
                        val.plugin = kafka_data['plugin']
                        val.plugin_instance = kafka_data['plugin_instance']
                        val.type = kafka_data['type']
                        val.type_instance = kafka_data['type_instance']
                        val.value = kafka_data['values'][index]
                        val.interval = kafka_data['interval']
                        val.time = kafka_data['time']
                        val.ds_name = ds_name
                        collector.add(val)


def main():
    # Parsing cmdline options
    parser = argparse.ArgumentParser()
    parser.add_argument("--events-schema", dest="schema", required=True,
                        help="YAML events schema definition", metavar="FILE")
    parser.add_argument("--config", dest="configfile", default=None,
                        help="Specify config file", metavar="FILE")
    parser.add_argument("--loglevel", dest="level", default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help="Specify log level (default: %(default)s)",
                        metavar="LEVEL")
    parser.add_argument("--logfile", dest="logfile", default='ves_app.log',
                        help="Specify log file (default: %(default)s)",
                        metavar="FILE")
    args = parser.parse_args()

    # Create log file
    logging.basicConfig(filename=args.logfile,
                        format='%(asctime)s %(message)s',
                        level=args.level)
    if args.configfile is None:
        logging.warning("No configfile specified, using default options")

    # Create Application Instance
    application_instance = VESApp()
    application_instance.init(args.configfile, args.schema)

    try:
        # Run the plugin
        application_instance.run()
    except KeyboardInterrupt:
        logging.info(" - Ctrl-C handled, exiting gracefully")
    except Exception as e:
        logging.error('{}, {}'.format(type(e), e))
    finally:
        application_instance.destroy()
        sys.exit()


if __name__ == '__main__':
    main()
