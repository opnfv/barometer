# -*- coding: utf-8 -*-
#
# Copyright 2017 OPNFV
#
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

"""Executing test of plugins"""

import requests
from keystoneclient.v3 import client
import os
import sys
import time
import logging
import config_server
import tests
import local_agent
from distutils import version
from opnfv.deployment import factory

AODH_NAME = 'aodh'
GNOCCHI_NAME = 'gnocchi'
ID_RSA_SRC = '/root/.ssh/id_rsa'
ID_RSA_DST_DIR = '/root/.ssh'
ID_RSA_DST = ID_RSA_DST_DIR + '/id_rsa'
APEX_IP = os.getenv("INSTALLER_IP").rstrip('\n')
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


def get_apex_nodes():
    handler = factory.Factory.get_handler('apex',
                                          APEX_IP,
                                          APEX_USER_STACK,
                                          APEX_PKEY)
    nodes = handler.get_nodes()
    return nodes


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
            url = self._gnocchi_url + ('/v2/metric?limit=400')
        else:
            url = self._gnocchi_url \
                + ('/v3/metric/%s?q.field=metric&limit=400' % criteria)
        headers = {'X-Auth-Token': self._auth_token}
        resp = requests.get(url, headers=headers)
        try:
            resp.raise_for_status()
            self._meter_list = resp.json()
        except (KeyError, ValueError, requests.exceptions.HTTPError) as err:
            raise InvalidResponse(err, resp)


class AodhClient(object):
    # Gnocchi Client to authenticate and request meters
    def __init__(self):
        self._auth_token = None
        self._aodh_url = None
        self._meter_list = None

    def auth_token(self):
        # Get auth token
        self._auth_server()
        return self._auth_token

    def get_aodh_url(self):
        # Get Gnocchi  URL
        return self._gnocchi_url

    def get_aodh_metrics(self, criteria=None):
        # Subject to change if metric gathering is different for gnocchi
        self._request_meters(criteria)
        return self._meter_list

    def _auth_server(self):
        # Request token in authentication server
        logger.debug('Connecting to the AODH auth server {}'.format(
            os.environ['OS_AUTH_URL']))
        keystone = client.Client(username=os.environ['OS_USERNAME'],
                                 password=os.environ['OS_PASSWORD'],
                                 tenant_name=os.environ['OS_USERNAME'],
                                 auth_url=os.environ['OS_AUTH_URL'])
        self._auth_token = keystone.auth_token
        for service in keystone.service_catalog.get_data():
            if service['name'] == AODH_NAME:
                for service_type in service['endpoints']:
                    if service_type['interface'] == 'internal':
                        self._gnocchi_url = service_type['url']

        if self._aodh_url is None:
            logger.warning('Aodh is not registered in service catalog')


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
        compute_name = compute_node.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                date = node.run_cmd(
                    "date '+%Y-%m-%d'")
                hostname = node.run_cmd('hostname -A')
                hostname = hostname.split()[0]
                metrics = []
                for plugin_subdir in plugin_subdirectories:
                    for meter_category in meter_categories:
                        stdout1 = node.run_cmd(
                            "tail -2 /var/lib/collectd/csv/"
                            + "{0}/{1}/{2}-{3}".format(
                                hostname, plugin_subdir,
                                meter_category, date))
                        stdout2 = node.run_cmd(
                            "tail -1 /var/lib/collectd/csv/"
                            + "{0}/{1}/{2}-{3}".format(
                                hostname, plugin_subdir,
                                meter_category, date))
                        # Storing last two values
                        values = stdout1
                        values2 = stdout2
                        if values is None:
                            logger.error(
                                'Getting last two CSV entries of meter category'
                                + ' {0} in {1} subdir failed'.format(
                                    meter_category, plugin_subdir))
                        elif values2 is None:
                            logger.error(
                                'Getting last CSV entries of meter category'
                                + ' {0} in {1} subdir failed'.format(
                                    meter_category, plugin_subdir))
                        else:
                            values = values.split(',')
                            old_value = float(values[0])
                            values2 = values2.split(',')
                            new_value = float(values2[0])
                            metrics.append((
                                plugin_subdir, meter_category, old_value,
                                new_value))
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


def _process_result(compute_node, out_plugin, test, result, results_list, node):
    """Print test result and append it to results list.

    Keyword arguments:
    test -- testcase name
    result -- boolean test result
    results_list -- results list
    """
    if result:
        logger.info(
            'Test case for {0} with {1} PASSED on {2}.'.format(
                node, out_plugin, test))
    else:
        logger.error(
            'Test case for {0} with {1} FAILED on {2}.'.format(
                node, out_plugin, test))
    results_list.append((compute_node, out_plugin, test, result))


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
        if out_plugin == 'Gnocchi':
            if (id, out_plugin, plugin, True) in results:
                print_line += ' PASS   |'
            elif (id, out_plugin, plugin, False) in results:
                print_line += ' FAIL   |'
            else:
                print_line += ' SKIP   |'
        elif out_plugin == 'AODH':
            if (id, out_plugin, plugin, True) in results:
                print_line += ' PASS   |'
            elif (id, out_plugin, plugin, False) in results:
                print_line += ' FAIL   |'
            else:
                print_line += ' SKIP   |'
        elif out_plugin == 'SNMP':
            if (id, out_plugin, plugin, True) in results:
                print_line += ' PASS   |'
            elif (id, out_plugin, plugin, False) in results:
                print_line += ' FAIL   |'
            else:
                print_line += ' SKIP   |'
        elif out_plugin == 'CSV':
            if (id, out_plugin, plugin, True) in results:
                print_line += ' PASS   |'
            elif (id, out_plugin, plugin, False) in results:
                print_line += ' FAIL   |'
            else:
                print_line += ' SKIP   |'
        else:
            print_line += ' SKIP   |'
    return print_line


def print_overall_summary(
        compute_ids, tested_plugins, aodh_plugins, results, out_plugins):
    """Print overall summary table.

    Keyword arguments:
    compute_ids -- list of compute IDs
    tested_plugins -- list of plug-ins
    results -- results list
    out_plugins --  list of used out plug-ins
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
        + ' OVERALL SUMMARY'
        + ' ' * (
            9*len(compute_node_names) - (9*len(compute_node_names))/2)
        + '|')
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))
    logger.info(line_of_nodes)
    logger.info(
        '+' + ('-' * 16) + '+' + (('-' * 8) + '+') * len(compute_node_names))
    out_plugins_print = []
    out_plugins_print1 = []
    for key in out_plugins.keys():
        if 'Gnocchi' in out_plugins[key]:
            out_plugins_print1.append('Gnocchi')
        if 'AODH' in out_plugins[key]:
            out_plugins_print1.append('AODH')
        if 'SNMP' in out_plugins[key]:
            out_plugins_print1.append('SNMP')
        if 'CSV' in out_plugins[key]:
            out_plugins_print1.append('CSV')
    for i in out_plugins_print1:
        if i not in out_plugins_print:
            out_plugins_print.append(i)
    for out_plugin in out_plugins_print:
        output_plugins_line = ''
        for id in compute_ids:
            out_plugin_result = '----'
            if out_plugin == 'Gnocchi':
                out_plugin_result = \
                    'PASS'
            elif out_plugin == 'AODH':
                out_plugin_result = \
                    'PASS'
            elif out_plugin == 'SNMP':
                out_plugin_result = \
                    'PASS'
            elif out_plugin == 'CSV':
                out_plugin_result = \
                    'PASS' if [
                        plugin for comp_id, out_pl, plugin, res in results
                        if comp_id == id and res] else 'FAIL'
            else:
                out_plugin_result = \
                    'FAIL'
            output_plugins_line += '| ' + out_plugin_result + '   '
        logger.info(
            '| OUT:{}'.format(out_plugin) + (' ' * (11 - len(out_plugin)))
            + output_plugins_line + '|')

        if out_plugin == 'AODH':
            for plugin in sorted(aodh_plugins.values()):
                line_plugin = _print_final_result_of_plugin(
                    plugin, compute_ids, results, out_plugins, out_plugin)
                logger.info(
                    '|  IN:{}'.format(plugin) + (' ' * (11-len(plugin)))
                    + '|' + line_plugin)
        else:
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
        test_labels, name, out_plugin, controllers, compute_node,
        conf, results, error_plugins, out_plugins):
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
        'mcelog': [(
            conf.is_mcelog_installed(compute_node, 'mcelog'),
            'mcelog must be installed.')],
        'ovs_events': [(
            len(ovs_existing_configured_int) > 0 or len(ovs_interfaces) > 0,
            'Interfaces must be configured.')],
        'ovs_stats': [(
            len(ovs_existing_configured_bridges) > 0,
            'Bridges must be configured.')]}
    gnocchi_criteria_lists = {
        'hugepages': 'hugepages',
        'intel_rdt': 'rdt',
        'mcelog': 'mcelog',
        'ovs_events': 'interface-ovs-system',
        'ovs_stats': 'ovs_stats-br0.br0'}
    aodh_criteria_lists = {
        'mcelog': 'mcelog',
        'ovs_events': 'ovs_events'}
    snmp_mib_files = {
        'intel_rdt': '/usr/share/snmp/mibs/Intel-Rdt.txt',
        'hugepages': '/usr/share/snmp/mibs/Intel-Hugepages.txt',
        'mcelog': '/usr/share/snmp/mibs/Intel-Mcelog.txt'}
    snmp_mib_strings = {
        'intel_rdt': 'INTEL-RDT-MIB::rdtLlc.1',
        'hugepages': 'INTEL-HUGEPAGES-MIB::hugepagesPageFree',
        'mcelog': 'INTEL-MCELOG-MIB::memoryCorrectedErrors.1'}
    nr_hugepages = int(time.time()) % 10000
    snmp_in_commands = {
        'intel_rdt': None,
        'hugepages': 'echo {} > /sys/kernel/'.format(nr_hugepages)
                     + 'mm/hugepages/hugepages-2048kB/nr_hugepages',
        'mcelog': '/root/mce-inject_df < /root/corrected'}
    csv_subdirs = {
        'intel_rdt': [
            'intel_rdt-0-2'],
        'hugepages': [
            'hugepages-mm-2048Kb', 'hugepages-node0-2048Kb',],
        # 'ipmi': ['ipmi'],
        'mcelog': [
            'mcelog-SOCKET_0_CHANNEL_0_DIMM_any',
            'mcelog-SOCKET_0_CHANNEL_any_DIMM_any'],
        'ovs_stats': [
            'ovs_stats-br0.br0'],
        'ovs_events': [
            'ovs_events-br0']}
    # csv_meter_categories_ipmi = get_csv_categories_for_ipmi(conf,
    # compute_node)
    csv_meter_categories = {
        'intel_rdt': [
            'bytes-llc', 'ipc'],
        'hugepages': ['vmpage_number-free', 'vmpage_number-used'],
        # 'ipmi': csv_meter_categories_ipmi,
        'mcelog': [
            'errors-corrected_memory_errors',
            'errors-uncorrected_memory_errors'],
        'ovs_stats': [
            'if_dropped', 'if_errors', 'if_packets'],
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
            compute_node.get_id(), out_plugin, test_labels[name], False,
            results, compute_node.get_name())
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
        # optional plugin
        elif "intel_rdt" == name and not conf.is_rdt_available(compute_node):
            #TODO: print log message
            logger.info("RDT is not available on virtual nodes, skipping test.")
            res = True
            print("Results for {}, pre-processing".format(str(test_labels[name])))
            print(results)
            _process_result(
                compute_node.get_id(), out_plugin, test_labels[name],
                res, results, compute_node.get_name())
            print("Results for {}, post-processing".format(str(test_labels[name])))
            print(results)
        else:
            plugin_interval = conf.get_plugin_interval(compute_node, name)
            if out_plugin == 'Gnocchi':
                res = conf.test_plugins_with_gnocchi(
                    compute_node.get_name(), plugin_interval,
                    logger, criteria_list=gnocchi_criteria_lists[name])
            if out_plugin == 'AODH':
                res = conf.test_plugins_with_aodh(
                    compute_node.get_name(), plugin_interval,
                    logger, criteria_list=aodh_criteria_lists[name])
            if out_plugin == 'SNMP':
                res = \
                    name in snmp_mib_files and name in snmp_mib_strings \
                    and conf.test_plugins_with_snmp(
                        compute_node.get_name(), plugin_interval, logger, name,
                        snmp_mib_files[name], snmp_mib_strings[name],
                        snmp_in_commands[name])
            if out_plugin == 'CSV':
                res = tests.test_csv_handles_plugin_data(
                    compute_node, conf.get_plugin_interval(compute_node, name),
                    name, csv_subdirs[name], csv_meter_categories[name],
                    logger, CSVClient(conf))

            if res and plugin_errors:
                logger.info(
                    'Test works, but will be reported as failure,'
                    + 'because of non-critical errors.')
                res = False
            print("Results for {}, pre-processing".format(str(test_labels[name])))
            print(results)
            _process_result(
                compute_node.get_id(), out_plugin, test_labels[name],
                res, results, compute_node.get_name())
            print("Results for {}, post-processing".format(str(test_labels[name])))
            print(results)


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


def create_ovs_bridge():
    """Create OVS brides on compute nodes"""
    handler = factory.Factory.get_handler('apex',
                                          APEX_IP,
                                          APEX_USER_STACK,
                                          APEX_PKEY)
    nodes = handler.get_nodes()
    logger.info("Creating OVS bridges on computes nodes")
    for node in nodes:
        if node.is_compute():
            node.run_cmd('sudo ovs-vsctl add-br br0')
            node.run_cmd('sudo ovs-vsctl set-manager ptcp:6640')
    logger.info('OVS Bridges created on compute nodes')


def mcelog_install():
    """Install mcelog on compute nodes."""
    _print_label('Enabling mcelog and OVS bridges on compute nodes')
    handler = factory.Factory.get_handler('apex',
                                          APEX_IP,
                                          APEX_USER_STACK,
                                          APEX_PKEY)
    nodes = handler.get_nodes()
    mce_bin = os.path.dirname(os.path.realpath(__file__)) + '/mce-inject_ea'
    for node in nodes:
        if node.is_compute():
            centos_release = node.run_cmd('uname -r')
            if version.LooseVersion(centos_release) < version.LooseVersion('3.10.0-514.26.2.el7.x86_64'):
                logger.info(
                    'Mcelog will NOT be enabled on node-{}.'
                    + ' Unsupported CentOS release found ({}).'.format(
                        node.get_dict()['name'],centos_release))
            else:
                logger.info(
                    'Checking if mcelog is enabled'
                    + ' on node-{}...'.format(node.get_dict()['name']))
                res = node.run_cmd('ls')
                if 'mce-inject_ea' and 'corrected' in res:
                    logger.info(
                        'Mcelog seems to be already installed '
                        + 'on node-{}.'.format(node.get_dict()['name']))
                    node.run_cmd('sudo modprobe mce-inject')
                    node.run_cmd('sudo ./mce-inject_ea < corrected')
                else:
                    logger.info(
                        'Mcelog will be enabled '
                        + 'on node-{}...'.format(node.get_dict()['name']))
                    node.put_file(mce_bin, 'mce-inject_ea')
                    node.run_cmd('chmod a+x mce-inject_ea')
                    node.run_cmd('echo "CPU 0 BANK 0" > corrected')
                    node.run_cmd(
                        'echo "STATUS 0xcc00008000010090" >>'
                        + ' corrected')
                    node.run_cmd(
                        'echo "ADDR 0x0010FFFFFFF" >> corrected')
                    node.run_cmd('sudo modprobe mce-inject')
                    node.run_cmd('sudo ./mce-inject_ea < corrected')
                    logger.info(
                        'Mcelog was installed '
                        + 'on node-{}.'.format(node.get_dict()['name']))



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
            node.run_cmd('sudo systemctl restart mcelog')
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
    logger.info('controllers: {}'.format([('{0}: {1}'.format(
        node.get_name(), node.get_ip())) for node in controllers]))
    logger.info('computes: {}'.format([('{0}: {1}'.format(
        node.get_name(), node.get_ip())) for node in computes]))

    mcelog_install()
    create_ovs_bridge()
    gnocchi_running_on_con = False
    aodh_running_on_con = False
    # Disabling SNMP write plug-in
    snmp_running = False
    _print_label('Testing Gnocchi and AODH plugins on nodes')

    for controller in controllers:
        gnocchi_running = (
            gnocchi_running_on_con or conf.is_gnocchi_running(controller))
        aodh_running = (
            aodh_running_on_con or conf.is_aodh_running(controller))

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
    aodh_plugin_labels = {
        'mcelog': 'Mcelog',
        'ovs_events': 'OVS events'}
    out_plugins = {}
    for compute_node in computes:
        node_id = compute_node.get_id()
        node_name = compute_node.get_name()
        out_plugins[node_id] = []
        compute_ids.append(node_id)
        compute_node_names.append(node_name)
        plugins_to_enable = []
        error_plugins = []
        gnocchi_running_com = (
            gnocchi_running and conf.check_gnocchi_plugin_included(
                compute_node))
        aodh_running_com = (
            aodh_running and conf.check_aodh_plugin_included(compute_node))
        # logger.info("SNMP enabled on {}" .format(node_name))
        if gnocchi_running_com:
            out_plugins[node_id].append("Gnocchi")
        if aodh_running_com:
            out_plugins[node_id].append("AODH")
        if snmp_running:
            out_plugins[node_id].append("SNMP")

        if 'Gnocchi' in out_plugins[node_id]:
            plugins_to_enable.append('csv')
            out_plugins[node_id].append("CSV")
            if plugins_to_enable:
                _print_label(
                    'NODE {}: Enabling Test Plug-in '.format(node_name)
                    + 'and Test case execution')
            if plugins_to_enable and not conf.enable_plugins(
                    compute_node, plugins_to_enable, error_plugins,
                    create_backup=False):
                logger.error(
                    'Failed to test plugins on node {}.'.format(node_id))
                logger.info(
                    'Testcases on node {} will not be executed'.format(
                        node_id))

        for i in out_plugins[node_id]:
            if i == 'AODH':
                for plugin_name in sorted(aodh_plugin_labels.keys()):
                    _exec_testcase(
                        aodh_plugin_labels, plugin_name, i,
                        controllers, compute_node, conf, results,
                        error_plugins, out_plugins[node_id])
            elif i == 'CSV':
                _print_label("Node {}: Executing CSV Testcases".format(
                    node_name))
                logger.info("Restarting collectd for CSV tests")
                collectd_restarted, collectd_warnings = \
                    conf.restart_collectd(compute_node)
                sleep_time = 10
                logger.info(
                    'Sleeping for {} seconds'.format(sleep_time)
                    + ' after collectd restart...')
                time.sleep(sleep_time)
                if not collectd_restarted:
                    for warning in collectd_warnings:
                        logger.warning(warning)
                    logger.error(
                        'Restart of collectd on node {} failed'.format(
                            compute_node))
                    logger.info(
                        'CSV Testcases on node {}'.format(compute_node)
                        + ' will not be executed.')
                for plugin_name in sorted(plugin_labels.keys()):
                    _exec_testcase(
                        plugin_labels, plugin_name, i,
                        controllers, compute_node, conf, results,
                        error_plugins, out_plugins[node_id])

            else:
                for plugin_name in sorted(plugin_labels.keys()):
                    _exec_testcase(
                        plugin_labels, plugin_name, i,
                        controllers, compute_node, conf, results,
                        error_plugins, out_plugins[node_id])

    mcelog_delete()
    print_overall_summary(
        compute_ids, plugin_labels, aodh_plugin_labels, results, out_plugins)

    res_overall = 0
    for res in results:
        if not res[3]:
            logger.error('Some tests have failed or have not been executed')
            logger.error('Overall Result is Fail')
            res_overall = 1
        else:
            pass

    _print_label('Testing LocalAgent on compute nodes')
    res_agent = local_agent.local_agent_main(logger, conf, computes)

    return 0 if res_overall == 0 and res_agent == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
