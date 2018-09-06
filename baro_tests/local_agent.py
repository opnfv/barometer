# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# Patch on October 10 2017

"""Executing test of LocalAgent"""

import os
import pika
import requests
import time

import tests

logger = None


class LocalAgentClient(object):
    """Client to request LocalAgent"""
    def __init__(self, host, port, user, passwd):
        """
        Keyword arguments:
        host -- Host URL
        port -- Host Port
        user -- Username
        passwd -- Password
        """
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd

    def set(self, file):
        logger.error('Do nothing to LocalAgent')

    def __str__(self):
        return ('host: {0}, port: {1}, user: {2}, pass: {3}'
                .format(self._host, self._port,
                        self._user, (self._passwd and '<Filterd>')))


class RestLocalAgentClient(LocalAgentClient):
    """Client to request LocalAgent using REST"""
    def __init__(self, host, port, user, passwd):
        super(self.__class__, self).__init__(host, port, user, passwd)

    def set(self, file):
        logger.debug('Send to localagent using REST -- {}'.format(str(self)))

        if not os.path.isfile(file):
            print '{} is not found'.format(file)
            return False
        filename = os.path.basename(file)

        url = 'http://{0}:{1}/collectd/conf'.format(self._host, self._port)
        config = {'file': (filename, open(file, 'r'))}
        requests.post(url, files=config)

        return True


class PubLocalAgentClient(LocalAgentClient):
    """Client to request LocalAgent using AMQP Publish"""
    def __init__(self, host, port, user, passwd):
        super(self.__class__, self).__init__(host, port, user, passwd)

    def set(self, file):
        logger.debug('Send to localagent using AMQP Publish -- {}'
                     .format(str(self)))

        if not os.path.isfile(file):
            print '{} is not found'.format(file)
            return False
        filename = os.path.basename(file)
        filebody = open(file, 'r').read()
        message = filename + '/' + filebody

        credentials = pika.PlainCredentials(self._user, self._passwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self._host, port=int(self._port),
                credentials=credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange='collectd-conf',
                                 exchange_type='fanout')
        channel.basic_publish(exchange='collectd-conf',
                              routing_key='',
                              body=message)

        connection.close()
        return True


def _process_localagent_result(compute_node, testfunc,
                               result, results_list, node):
    """Print LocalAgent test result and append it to results list.

    Keyword arguments:
    testfunc -- localagent function name
    result -- boolean test result
    results_list -- results list
    """
    if result:
        logger.info(
            'Test case for {0} with LocalAgent PASSED on {1}.'.format(
                node, testfunc))
    else:
        logger.error(
            'Test case for {0} with LocalAgent FAILED on {1}.'.format(
                node, testfunc))
    results_list.append((compute_node, "LocalAgent", testfunc, result))


def _print_result_of_localagent(compute_ids, results):
    """Print results of LocalAgent.

    Keyword arguments:
    compute_ids -- list of compute node IDs
    results -- results list
    """
    compute_node_names = ['Node-{}'.format(i) for i in range(
        len((compute_ids)))]
    all_computes_in_line = ''
    for compute in compute_node_names:
        all_computes_in_line += '| ' + compute + (' ' * (7 - len(compute)))
    line_of_nodes = '| Test           ' + all_computes_in_line + '|'
    logger.info('=' * 70)
    logger.info('+' + ('-' * ((9 * len(compute_node_names))+16)) + '+')
    logger.info(
        '|' + ' ' * ((9*len(compute_node_names))/2)
        + ' LOCALAGENT TEST'
        + ' ' * (
            9*len(compute_node_names) - (9*len(compute_node_names))/2)
        + '|')
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))
    logger.info(line_of_nodes)
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))

    testname = "LocalAgent"
    print_line = ''
    for id in compute_ids:
        all_result = \
            'FAIL' if [
                testfunc for comp_id, testname, testfunc, res in results
                if comp_id == id and not res] else 'PASS'
        print_line += '| ' + all_result + '   '
    logger.info(
        '| {}'.format(testname) + (' ' * (15 - len(testname)))
        + print_line + '|')

    for testfunc in ['Server', 'InfoFetch']:
        print_line = ''
        for id in compute_ids:
            if (id, testname, testfunc, True) in results:
                print_line += ' PASS   |'
            elif (id, testname, testfunc, False) in results:
                print_line += ' FAIL   |'
            else:
                print_line += ' SKIP   |'
        logger.info(
            '|  {}'.format(testfunc) + (' ' * (14-len(testfunc)))
            + '|' + print_line)

    logger.info(
        '+' + ('-' * 16) + '+'
        + (('-' * 8) + '+') * len(compute_node_names))
    logger.info('=' * 70)


def local_agent_main(bt_logger, conf, computes):
    """Check LocalAgent of each compute node.

    Keyword arguments:
    bt_logger -- logger instance
    computes -- compute node list
    """
    global logger
    logger = bt_logger

    compute_ids = []
    agent_results = []
    for compute_node in computes:
        node_id = compute_node.get_id()
        compute_ids.append(node_id)

        agent_server_running = conf.is_localagent_server_running(compute_node)
        agent_infofetch_running = (
            conf.is_localagent_infofetch_running(compute_node) and
            conf.is_redis_running(compute_node))

        if agent_server_running:
            test_name = 'barotest'
            tmpfile = '/tmp/' + test_name + '.conf'

            agent_config = conf.get_localagent_config(compute_node)
            listen_ip = compute_node.get_ip()
            listen_port = agent_config.get('server').get('listen_port')
            amqp_host = agent_config.get('server').get('amqp_host')
            amqp_port = agent_config.get('server').get('amqp_port')
            amqp_user = agent_config.get('server').get('amqp_user')
            amqp_passwd = agent_config.get('server').get('amqp_password')
            rest_client = RestLocalAgentClient(
                              listen_ip, listen_port, '', '')
            pub_client = PubLocalAgentClient(
                             amqp_host, amqp_port, amqp_user,
                             amqp_passwd)

            all_res = True
            for client in [rest_client, pub_client]:
                tests.test_localagent_server_set_collectd(
                    compute_node, tmpfile, logger, client)
                sleep_time = 1
                logger.info(
                    'Sleeping for {} seconds'.format(sleep_time)
                    + ' before localagent server test...')
                time.sleep(sleep_time)
                res = conf.check_localagent_dummy_included(
                          compute_node, test_name)
                all_res = all_res and res

            _process_localagent_result(
                compute_node.get_id(), 'Server',
                all_res, agent_results, compute_node.get_name())

        if agent_infofetch_running:
            test_name = 'barotest'
            resources = conf.create_testvm(compute_node, test_name)
            sleep_time = 5
            logger.info(
                'Sleeping for {} seconds'.format(sleep_time)
                + ' before localagent infofetch test...')
            time.sleep(sleep_time)
            res = conf.test_localagent_infofetch_get_data(
                      compute_node, test_name)
            conf.delete_testvm(resources)

            _process_localagent_result(
                compute_node.get_id(), 'InfoFetch',
                res, agent_results, compute_node.get_name())

    _print_result_of_localagent(compute_ids, agent_results)

    for res in agent_results:
        if not res[3]:
            logger.error('Some tests have failed or have not been executed')
            logger.error('LocalAgent test is Fail')
            return 1
        else:
            pass
    return 0
