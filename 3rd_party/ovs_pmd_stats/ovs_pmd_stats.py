#!/usr/bin/env python
#
# Copyright(c) 2017 Intel Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
#   Roman Korynkevych <romanx.korynkevych@intel.com>

import socket
import argparse
import json
import logging

HOSTNAME = socket.gethostname()
PROG_NAME = 'ovs_pmd_stats'
TYPE = 'counter'

MAIN_THREAD = 'main thread'
PMD_THREAD = 'pmd thread'

REQUEST_MESSAGE = '{"id":0,"method":"dpif-netdev/pmd-stats-show","params":[]}'
RESPONSE_MESSAGE_TIMEOUT = 1.0

# Setup arguments
parser = argparse.ArgumentParser(prog=PROG_NAME)
parser.add_argument('--socket-pid-file', required=True, help='ovs-vswitchd.pid file location')
args = parser.parse_args()

try:
    fp = open(args.socket_pid_file, 'r')
    pid = fp.readline()
    fp.close()
except IOError as e:
    logging.error('I/O error({}): {}'.format(e.errno, e.strerror))
    raise SystemExit()
except:
    logging.error('Unexpected error:', sys.exc_info()[0])
    raise SystemExit()

server_address = args.socket_pid_file.replace('.pid', '.{}.ctl'.format(pid.strip()))

# open unix socket to ovs-vswitch
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    sock.connect(server_address)
except socket.error as msg:
    logging.error('Socket address: {} Error: {}'.format(server_address, msg))
    raise SystemExit()

# set timeout
sock.settimeout(RESPONSE_MESSAGE_TIMEOUT)

# send request
sock.sendall(REQUEST_MESSAGE)

# listen for respnse message
rdata = ''
while True:
    try:
        rdata += sock.recv(4096)

        if rdata.count('{') == rdata.count('}'):
          break
    except socket.timeout:
        logging.error('Response message has not been received in {} sec.'.format(RESPONSE_MESSAGE_TIMEOUT))
        raise SystemExit()
    except socket.error as e:
        logging.error('Error received while reading: {}'.format(e.strerror))
        raise SystemExit()

# parse the message
try:
    s = json.loads(rdata, strict=False)
except ValueError as e:
    logging.error('Failed to parse JSON response: {}'.format(e.strerror))
    raise SystemExit()

# check for key string presence in the string
if 'result' not in s or 'id' not in s or 'error' not in s:
    logging.error("One of the keys: ['id'], ['result'], ['error'] is missed in the response")
    logging.error('Msg: {}'.format(s))
    raise SystemExit()

array = s['result'].replace('\t', '').splitlines()

# submit metrics in collectd format
plugin_instance = ''
for el in array:
    if MAIN_THREAD in el or PMD_THREAD in el:
        plugin_instance = el[:-1].replace(' ', '_')
    else:
        type_instance = el.split(':')[0].replace(' ', "_")
        value = el.split(':')[1].strip().split(' ')[0]
        print('PUTVAL %s/%s-%s/%s-%s N:%s' % (HOSTNAME, PROG_NAME, plugin_instance, TYPE, type_instance, value))

# close socket
sock.close()
