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

"""Executing test of plugins"""

import requests
from keystoneclient.v3 import client
import os
import sys
import time
import logging
import config_server
import tests
from opnfv.deployment import factory

GNOCCHI_NAME = 'gnocchi'
ID_RSA_SRC = '/root/.ssh/id_rsa'
ID_RSA_DST_DIR = '/home/opnfv/.ssh'
ID_RSA_DST = ID_RSA_DST_DIR + '/id_rsa'
APEX_IP = 'undercloud'
APEX_USER = 'root'
APEX_USER_STACK = 'stack'
APEX_PKEY = '/root/.ssh/id_rsa'


class KeystoneException(Exception):
    """Keystone exception class"""
    def __init__(self, message, exc=None, response=None):
        """
        Keyword arguments:
        message -- error message
        exc -- exception
        response -- response
        """
        if exc:
            message += "\nReason: %s" % exc
        super(KeystoneException, self).__init__(message)

        self.response = response
        self.exception = exc


class InvalidResponse(KeystoneException):
    """Invalid Keystone exception class"""
    def __init__(self, exc, response):
        """
        Keyword arguments:
        exc -- exception
        response -- response
        """
        super(InvalidResponse, self).__init__(
            "Invalid response", exc, response)


class GnocchiClient(object):
    # Gnocchi Client to authenticate and request meters
    def __init__(self):
        self._auth_token = None
        self._gnocchi_url = None
        self._meter_list = None

    def auth_token(self):
        # Get auth token
        self._auth_server()
        return self._auth_token

    def get_gnocchi_url(self):
        # Get Gnocchi  URL
        return self._gnocchi_url

    def get_gnocchi_metrics(self, criteria=None):
        # Subject to change if metric gathering is different for gnocchi
        self._request_meters(criteria)
        return self._meter_list

    def _auth_server(self):
        # Request token in authentication server
        logger.debug('Connecting to the auth server {}'.format(
            os.environ['OS_AUTH_URL']))
        keystone = client.Client(username=os.environ['OS_USERNAME'],
                                 password=os.environ['OS_PASSWORD'],
                                 tenant_name=os.environ['OS_USERNAME'],
                                 auth_url=os.environ['OS_AUTH_URL'])
        self._auth_token = keystone.auth_token
        for service in keystone.service_catalog.get_data():
            if service['name'] == GNOCCHI_NAME:
                for service_type in service['endpoints']:
                    if service_type['interface'] == 'internal':
                        self._gnocchi_url = service_type['url']

        if self._gnocchi_url is None:
            logger.warning('Gnocchi is not registered in service catalog')

    def _request_meters(self, criteria):
        """Request meter list values from ceilometer

        Keyword arguments:
        criteria -- criteria for ceilometer meter list
        """
        if criteria is None:
            url = self._gnocchi_url + ('/v3/resource?limit=400')
        else:
            url = self._gnocchi_url \
                + ('/v3/resource/%s?q.field=resource_id&limit=400' % criteria)
        headers = {'X-Auth-Token': self._auth_token}
        resp = requests.get(url, headers=headers)
        try:
            resp.raise_for_status()
            self._meter_list = resp.json()
        except (KeyError, ValueError, requests.exceptions.HTTPError) as err:
            raise InvalidResponse(err, resp)


class CSVClient(object):
    """Client to request CSV meters"""
    def __init__(self, conf):
        """
        Keyword arguments:
        conf -- ConfigServer instance
        """
        self.conf = conf

    def get_csv_metrics(
            self, compute_node, plugin_subdirectories, meter_categories):
        """Get CSV metrics.

        Keyword arguments:
        compute_node -- compute node instance
        plugin_subdirectories -- list of subdirectories of plug-in
        meter_categories -- categories which will be tested

        Return list of metrics.
        """
        stdout = self.conf.execute_command(
            "date '+%Y-%m-%d'", compute_node.get_ip())
        date = stdout[0].strip()
        metrics = []
        for plugin_subdir in plugin_subdirectories:
            for meter_category in meter_categories:
                stdout = self.conf.execute_command(
                    "tail -2 /var/lib/collectd/csv/"
                    + "{0}.jf.intel.com/{1}/{2}-{3}".format(
                        compute_node.get_name(), plugin_subdir, meter_category,
                        date),
                    compute_node.get_ip())
                # Storing last two values
                values = stdout
                if len(values) < 2:
                    logger.error(
                        'Getting last two CSV entries of meter category '
                        + '{0} in {1} subdir failed'.format(
                            meter_category, plugin_subdir))
                else:
                    old_value = int(values[0][0:values[0].index('.')])
                    new_value = int(values[1][0:values[1].index('.')])
                    metrics.append((
                        plugin_subdir, meter_category, old_value, new_value))
        return metrics


def get_csv_categories_for_ipmi(conf, compute_node):
    """Get CSV metrics.

    Keyword arguments:
    compute_node -- compute node instance

    Return list of categories.
    """
    stdout = conf.execute_command(
        "date '+%Y-%m-%d'", compute_node.get_ip())
    date = stdout[0].strip()
    categories = conf.execute_command(
        "ls /var/lib/collectd/csv/{0}.jf.intel.com/ipmi | grep {1}".format(
            compute_node.get_name(), date), compute_node.get_ip())
    return [category.strip()[:-11] for category in categories]


def _process_result(compute_node, test, result, results_list):
    """Print test result and append it to results list.

    Keyword arguments:
    test -- testcase name
    result -- boolean test result
    results_list -- results list
    """
    if result:
        logger.info(
            'Compute node {0} test case {1} PASSED.'.format(
                compute_node, test))
    else:
        logger.error(
            'Compute node {0} test case {1} FAILED.'.format(
                compute_node, test))
    results_list.append((compute_node, test, result))


def _print_label(label):
    """Print label on the screen

    Keyword arguments:
    label -- label string
    """
    label = label.strip()
    length = 70
    if label != '':
        label = ' ' + label + ' '
    length_label = len(label)
    length1 = (length - length_label) / 2
    length2 = length - length_label - length1
    length1 = max(3, length1)
    length2 = max(3, length2)
    logger.info(('=' * length1) + label + ('=' * length2))


def _print_plugin_label(plugin, node_name):
    """Print plug-in label.

    Keyword arguments:
    plugin -- plug-in name
    node_id -- node ID
    """
    _print_label(
        'Node {0}: Plug-in {1} Test case execution'.format(node_name, plugin))


def _print_final_result_of_plugin(
        plugin, compute_ids, results, out_plugins, out_plugin):
    """Print final results of plug-in.

    Keyword arguments:
    plugin -- plug-in name
    compute_ids -- list of compute node IDs
    results -- results list
    out_plugins -- list of out plug-ins
    out_plugin -- used out plug-in
    """
    print_line = ''
    for id in compute_ids:
        if out_plugins[id] == out_plugin:
            if (id, plugin, True) in results:
                print_line += ' PASS   |'
            elif (id, plugin, False) in results \
                    and out_plugins[id] == out_plugin:
                print_line += ' FAIL   |'
            else:
                print_line += ' NOT EX |'
        elif out_plugin == 'Gnocchi':
            print_line += ' NOT EX |'
        else:
            print_line += ' SKIP   |'
    return print_line


def print_overall_summary(compute_ids, tested_plugins, results, out_plugins):
    """Print overall summary table.

    Keyword arguments:
    compute_ids -- list of compute IDs
    tested_plugins -- list of plug-ins
    results -- results list
    out_plugins --  list of used out plug-ins
    """
    compute_node_names = ['Node-{}'.format(i) for i in range(
        len((compute_ids)))]
    # compute_node_names = ['Node-{}'.format(id) for id in compute_ids]
    all_computes_in_line = ''
    for compute in compute_node_names:
        all_computes_in_line += '| ' + compute + (' ' * (7 - len(compute)))
    line_of_nodes = '| Test           ' + all_computes_in_line + '|'
    logger.info('=' * 70)
    logger.info('+' + ('-' * ((9 * len(compute_node_names))+16)) + '+')
    logger.info(
        '|' + ' ' * ((9*len(compute_node_names))/2)
        + ' OVERALL SUMMARY'
        + ' ' * (
            9*len(compute_node_names) - (9*len(compute_node_names))/2)
        + '|')
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))
    logger.info(line_of_nodes)
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))
    out_plugins_print = ['Gnocchi']
    if 'SNMP' in out_plugins.values():
        out_plugins_print.append('SNMP')
    if 'CSV' in out_plugins.values():
        out_plugins_print.append('CSV')
    for out_plugin in out_plugins_print:
        output_plugins_line = ''
        for id in compute_ids:
            out_plugin_result = '----'
            if out_plugin == 'Gnocchi':
                out_plugin_result = \
                    'PASS' if out_plugins[id] == out_plugin else 'FAIL'
            if out_plugin == 'SNMP':
                if out_plugins[id] == out_plugin:
                    out_plugin_result = \
                        'PASS' if out_plugins[id] == out_plugin else 'FAIL'
                else:
                    out_plugin_result = 'SKIP'
            if out_plugin == 'CSV':
                if out_plugins[id] == out_plugin:
                    out_plugin_result = \
                        'PASS' if [
                            plugin for comp_id, plugin, res in results
                            if comp_id == id and res] else 'FAIL'
                else:
                    out_plugin_result = 'SKIP'
            output_plugins_line += '| ' + out_plugin_result + '   '
        logger.info(
            '| OUT:{}'.format(out_plugin) + (' ' * (11 - len(out_plugin)))
            + output_plugins_line + '|')
        for plugin in sorted(tested_plugins.values()):
            line_plugin = _print_final_result_of_plugin(
                plugin, compute_ids, results, out_plugins, out_plugin)
            logger.info(
                '|  IN:{}'.format(plugin) + (' ' * (11-len(plugin)))
                + '|' + line_plugin)
        logger.info(
            '+' + ('-' * 16) + '+'
            + (('-' * 8) + '+') * len(compute_node_names))
    logger.info('=' * 70)


def _exec_testcase(
        test_labels, name, gnocchi_running, compute_node,
        conf, results, error_plugins):
    """Execute the testcase.

    Keyword arguments:
    test_labels -- dictionary of plug-in IDs and their display names
    name -- plug-in ID, key of test_labels dictionary
    ceilometer_running -- boolean indicating whether Ceilometer is running
    compute_node -- compute node ID
    conf -- ConfigServer instance
    results -- results list
    error_plugins -- list of tuples with plug-in errors
        (plugin, error_description, is_critical):
        plugin -- plug-in ID, key of test_labels dictionary
        error_decription -- description of the error
        is_critical -- boolean value indicating whether error is critical
    """
    ovs_interfaces = conf.get_ovs_interfaces(compute_node)
    ovs_configured_interfaces = conf.get_plugin_config_values(
        compute_node, 'ovs_events', 'Interfaces')
    ovs_configured_bridges = conf.get_plugin_config_values(
         compute_node, 'ovs_stats', 'Bridges')
    ovs_existing_configured_int = [
        interface for interface in ovs_interfaces
        if interface in ovs_configured_interfaces]
    ovs_existing_configured_bridges = [
        bridge for bridge in ovs_interfaces
        if bridge in ovs_configured_bridges]
    plugin_prerequisites = {
        'intel_rdt': [(
            conf.is_libpqos_on_node(compute_node),
            'libpqos must be installed.')],
        'mcelog': [(
            conf.is_installed(compute_node, 'mcelog'),
            'mcelog must be installed.')],
        'ovs_events': [(
            len(ovs_existing_configured_int) > 0 or len(ovs_interfaces) > 0,
            'Interfaces must be configured.')],
        'ovs_stats': [(
            len(ovs_existing_configured_bridges) > 0,
            'Bridges must be configured.')]}
    ceilometer_criteria_lists = {
        'intel_rdt': [
            'intel_rdt.ipc', 'intel_rdt.bytes',
            'intel_rdt.memory_bandwidth'],
        'hugepages': ['hugepages.vmpage_number'],
        'ipmi': ['ipmi.temperature', 'ipmi.voltage'],
        'mcelog': ['mcelog.errors'],
        'ovs_stats': ['interface.if_packets'],
        'ovs_events': ['ovs_events.gauge']}
    ceilometer_substr_lists = {
        'ovs_events': ovs_existing_configured_int if len(
            ovs_existing_configured_int) > 0 else ovs_interfaces}
    csv_subdirs = {
        'intel_rdt': [
            'intel_rdt-{}'.format(core)
            for core in conf.get_plugin_config_values(
                compute_node, 'intel_rdt', 'Cores')],
        'hugepages': [
            'hugepages-mm-2048Kb', 'hugepages-node0-2048Kb',
            'hugepages-node1-2048Kb', 'hugepages-mm-1048576Kb',
            'hugepages-node0-1048576Kb', 'hugepages-node1-1048576Kb'],
        'ipmi': ['ipmi'],
        'mcelog': [
            'mcelog-SOCKET_0_CHANNEL_0_DIMM_any',
            'mcelog-SOCKET_0_CHANNEL_any_DIMM_any'],
        'ovs_stats': [
            'ovs_stats-{0}.{0}'.format(interface)
            for interface in ovs_existing_configured_bridges],
        'ovs_events': [
            'ovs_events-{}'.format(interface)
            for interface in (
                ovs_existing_configured_int
                if len(ovs_existing_configured_int) > 0 else ovs_interfaces)]}
    csv_meter_categories_ipmi = get_csv_categories_for_ipmi(conf, compute_node)
    csv_meter_categories = {
        'intel_rdt': [
            'bytes-llc', 'ipc', 'memory_bandwidth-local',
            'memory_bandwidth-remote'],
        'hugepages': ['vmpage_number-free', 'vmpage_number-used'],
        'ipmi': csv_meter_categories_ipmi,
        'mcelog': [
            'errors-corrected_memory_errors',
            'errors-uncorrected_memory_errors',
            'errors-corrected_memory_errors_in_24h',
            'errors-uncorrected_memory_errors_in_24h'],
        'ovs_stats': [
            'if_collisions', 'if_dropped', 'if_errors', 'if_packets',
            'if_rx_errors-crc', 'if_rx_errors-frame', 'if_rx_errors-over',
            'if_rx_octets', 'if_tx_octets'],
        'ovs_events': ['gauge-link_status']}

    _print_plugin_label(
        test_labels[name] if name in test_labels else name,
        compute_node.get_name())
    plugin_critical_errors = [
        error for plugin, error, critical in error_plugins
        if plugin == name and critical]
    if plugin_critical_errors:
        logger.error('Following critical errors occurred:'.format(name))
        for error in plugin_critical_errors:
            logger.error(' * ' + error)
        _process_result(
            compute_node.get_id(), test_labels[name], False, results)
    else:
        plugin_errors = [
            error for plugin, error, critical in error_plugins
            if plugin == name and not critical]
        if plugin_errors:
            logger.warning('Following non-critical errors occured:')
            for error in plugin_errors:
                logger.warning(' * ' + error)
        failed_prerequisites = []
        if name in plugin_prerequisites:
            failed_prerequisites = [
                prerequisite_name for prerequisite_passed,
                prerequisite_name in plugin_prerequisites[name]
                if not prerequisite_passed]
        if failed_prerequisites:
            logger.error(
                '{} test will not be executed, '.format(name)
                + 'following prerequisites failed:')
            for prerequisite in failed_prerequisites:
                logger.error(' * {}'.format(prerequisite))
        else:
            if gnocchi_running:
                res = conf.test_plugins_with_gnocchi(
                    compute_node.get_id(),
                    conf.get_plugin_interval(compute_node, name),
                    logger, client=GnocchiClient(),
                    criteria_list=ceilometer_criteria_lists[name],
                    resource_id_substrings=(
                        ceilometer_substr_lists[name]
                        if name in ceilometer_substr_lists else ['']))
            else:
                res = tests.test_csv_handles_plugin_data(
                    compute_node, conf.get_plugin_interval(compute_node, name),
                    name, csv_subdirs[name], csv_meter_categories[name],
                    logger, CSVClient(conf))
            if res and plugin_errors:
                logger.info(
                    'Test works, but will be reported as failure,'
                    + 'because of non-critical errors.')
                res = False
            _process_result(
                compute_node.get_id(), test_labels[name], res, results)


def get_results_for_ovs_events(
        plugin_labels, plugin_name, gnocchi_running,
        compute_node, conf, results, error_plugins):
    """ Testing OVS Events with python plugin
    """
    plugin_label = 'OVS events'
    res = conf.enable_ovs_events(
        compute_node, plugin_label, error_plugins, create_backup=False)
    _process_result(
        compute_node.get_id(), plugin_label, res, results)
    logger.info("Results for OVS Events = {}" .format(results))


def mcelog_install():
    """Install mcelog on compute nodes."""
    _print_label('Enabling mcelog on compute nodes')
    handler = factory.Factory.get_handler('apex',
                                          APEX_IP,
                                          APEX_USER_STACK,
                                          APEX_PKEY)
    nodes = handler.get_nodes()
    for node in nodes:
        if node.is_compute():
            centos_release = node.run_cmd('uname -r')
            if '3.10.0-514.26.2.el7.x86_64' not in centos_release:
                logger.info(
                    'Mcelog will not be enabled '
                    + 'on node-{0}, '.format(node.get_dict()['id'])
                    + 'unsupported CentOS release found ({1}).'.format(
                        centos_release))
            else:
                logger.info(
                    'Checking if  mcelog is enabled'
                    + ' on node-{}...'.format(node.get_dict()['id']))
                res = node.run_cmd('ls')
            if 'mce-inject_ea' and 'corrected' in res:
                logger.info(
                    'Mcelog seems to be already installed '
                    + 'on node-{}.'.format(node.get_dict()['id']))
                node.run_cmd('modprobe mce-inject_ea')
                node.run_cmd('mce-inject_ea < corrected')
            else:
                logger.info(
                    'Mcelog will be enabled on node-{}...'.format(
                        node.get_dict()['id']))
                node.put_file(
                    '/usr/local/lib/python2.7/dist-packages/baro_tests/'
                    + 'mce-inject_ea', 'mce-inject_ea')
                node.run_cmd('chmod a+x mce-inject_ea')
                node.run_cmd('echo "CPU 0 BANK 0" > corrected')
                node.run_cmd(
                    'echo "STATUS 0xcc00008000010090" >>'
                    + ' corrected')
                node.run_cmd(
                    'echo "ADDR 0x0010FFFFFFF" >> corrected')
                node.run_cmd('modprobe mce-inject')
                node.run_cmd('mce-inject_ea < corrected')
    logger.info('Mcelog is installed on all compute nodes')


def mcelog_delete():
    """Uninstall mcelog from compute nodes."""
    handler = factory.Factory.get_handler(
            'apex', APEX_IP, APEX_USER, APEX_PKEY)
    nodes = handler.get_nodes()
    for node in nodes:
        if node.is_compute():
            output = node.run_cmd('ls')
            if 'mce-inject_ea' in output:
                node.run_cmd('rm mce-inject_ea')
            if 'corrected' in output:
                node.run_cmd('rm corrected')
            node.run_cmd('systemctl restart mcelog')
    logger.info('Mcelog is deleted from all compute nodes')


def get_ssh_keys():
    if not os.path.isdir(ID_RSA_DST_DIR):
        os.makedirs(ID_RSA_DST_DIR)
    if not os.path.isfile(ID_RSA_DST):
        logger.info(
            "RSA key file {} doesn't exist".format(ID_RSA_DST)
            + ", it will be downloaded from installer node.")
        handler = factory.Factory.get_handler(
            'apex', APEX_IP, APEX_USER, APEX_PKEY)
        apex = handler.get_installer_node()
        apex.get_file(ID_RSA_SRC, ID_RSA_DST)
    else:
        logger.info("RSA key file {} exists.".format(ID_RSA_DST))


def _check_logger():
    """Check whether there is global logger available and if not, define one."""
    if 'logger' not in globals():
        global logger
        logger = logger.Logger("barometercollectd").getLogger()


def main(bt_logger=None):
    """Check each compute node sends gnocchi metrics.

    Keyword arguments:
    bt_logger -- logger instance
    """
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("stevedore").setLevel(logging.WARNING)
    logging.getLogger("opnfv.deployment.manager").setLevel(logging.WARNING)
    if bt_logger is None:
        _check_logger()
    else:
        global logger
        logger = bt_logger
    _print_label("Starting barometer tests suite")
    get_ssh_keys()
    conf = config_server.ConfigServer(APEX_IP, APEX_USER, logger)
    controllers = conf.get_controllers()
    if len(controllers) == 0:
        logger.error('No controller nodes found!')
        return 1
    computes = conf.get_computes()
    if len(computes) == 0:
        logger.error('No compute nodes found!')
        return 1

    _print_label(
        'Display of Control and Compute nodes available in the set up')
    logger.info('controllers: {}'.format([('{0}: {1} ({2})'.format(
        node.get_id(), node.get_name(),
        node.get_ip())) for node in controllers]))
    logger.info('computes: {}'.format([('{0}: {1} ({2})'.format(
        node.get_id(), node.get_name(), node.get_ip()))
        for node in computes]))

    mcelog_install()
    gnocchi_running_on_con = False
    _print_label('Test Gnocchi on controller nodes')

    for controller in controllers:
        logger.info("Controller = {}" .format(controller))
        gnocchi_client = GnocchiClient()
        gnocchi_client.auth_token()
        gnocchi_running_on_con = (
            gnocchi_running_on_con or conf.is_gnocchi_running(
                controller))
    if gnocchi_running_on_con:
        logger.info("Gnocchi is running on controller.")
    else:
        logger.error("Gnocchi is not running on controller.")
        logger.info("CSV will be enabled on compute nodes.")

    compute_ids = []
    compute_node_names = []
    results = []
    plugin_labels = {
        'intel_rdt': 'Intel RDT',
        'hugepages': 'Hugepages',
        # 'ipmi': 'IPMI',
        'mcelog': 'Mcelog',
        'ovs_stats': 'OVS stats',
        'ovs_events': 'OVS events'}
    out_plugins = {}
    for compute_node in computes:
        node_id = compute_node.get_id()
        node_name = compute_node.get_name()
        out_plugins[node_id] = 'CSV'
        compute_ids.append(node_id)
        compute_node_names.append(node_name)
        plugins_to_enable = []
        _print_label('NODE {}: Test Gnocchi Plug-in'.format(node_name))
        logger.info('Checking if gnocchi plug-in is included in compute nodes.')
        if not conf.check_gnocchi_plugin_included(compute_node):
            logger.error('Gnocchi plug-in is not included.')
            logger.info(
                'Testcases on node {} will not be executed'.format(node_name))
        else:
            collectd_restarted, collectd_warnings = \
                conf.restart_collectd(compute_node)
            sleep_time = 5
            logger.info(
                'Sleeping for {} seconds after collectd restart...'.format(
                    sleep_time))
            time.sleep(sleep_time)
            if not collectd_restarted:
                for warning in collectd_warnings:
                    logger.warning(warning)
                logger.error(
                    'Restart of collectd on node {} failed'.format(node_name))
                logger.info(
                    'Testcases on node {} will not be executed'.format(
                        node_name))
            else:
                for warning in collectd_warnings:
                    logger.warning(warning)
                gnocchi_running = (
                    gnocchi_running_on_con
                    and conf.test_gnocchi_is_sending_data(
                        controller))
                if gnocchi_running:
                    out_plugins[node_id] = 'Gnocchi'
                    logger.info("Gnocchi is active and collecting data")
                else:
                    plugins_to_enable.append('csv')
                    out_plugins[node_id] = 'CSV'
                    logger.error("Gnocchi is inactive and not collecting data")
                    logger.info(
                        "CSV will be enabled for verification "
                        + "of test plugins.")
                if plugins_to_enable:
                    _print_label(
                        'NODE {}: Enabling Test Plug-in '.format(node_name)
                        + 'and Test case execution')
                error_plugins = []
                if plugins_to_enable and not conf.enable_plugins(
                        compute_node, plugins_to_enable, error_plugins,
                        create_backup=False):
                    logger.error(
                        'Failed to test plugins on node {}.'.format(node_id))
                    logger.info(
                        'Testcases on node {} will not be executed'.format(
                            node_id))
                else:
                    if plugins_to_enable:
                        collectd_restarted, collectd_warnings = \
                            conf.restart_collectd(compute_node)
                        sleep_time = 30
                        logger.info(
                            'Sleeping for {} seconds'.format(sleep_time)
                            + ' after collectd restart...')
                        time.sleep(sleep_time)
                    if plugins_to_enable and not collectd_restarted:
                        for warning in collectd_warnings:
                            logger.warning(warning)
                        logger.error(
                            'Restart of collectd on node {} failed'.format(
                                node_id))
                        logger.info(
                            'Testcases on node {}'.format(node_id)
                            + ' will not be executed.')
                    else:
                        if collectd_warnings:
                            for warning in collectd_warnings:
                                logger.warning(warning)

                        for plugin_name in sorted(plugin_labels.keys()):
                            _exec_testcase(
                                plugin_labels, plugin_name,
                                gnocchi_running,
                                compute_node, conf, results, error_plugins)

            _print_label('NODE {}: Restoring config file'.format(node_name))
            conf.restore_config(compute_node)
        mcelog_delete()
    print_overall_summary(compute_ids, plugin_labels, results, out_plugins)

    if ((len([res for res in results if not res[2]]) > 0)
            or (len(results) < len(computes) * len(plugin_labels))):
        logger.error('Some tests have failed or have not been executed')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
