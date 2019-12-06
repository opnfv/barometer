# -*- coding: utf-8 -*-
#
# Copyright(c) 2017-2019 Intel Corporation and OPNFV. All rights reserved.
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
#
# SPDX-License-Identifier: Apache-2.0
#

"""Classes used by collectd.py"""

import time
import os.path
import os
import re
import yaml

from opnfv.deployment import factory
import paramiko
from functest.utils import constants

ID_RSA_PATH = '/root/.ssh/id_rsa'
SSH_KEYS_SCRIPT = '/home/opnfv/barometer/baro_utils/get_ssh_keys.sh'
DEF_PLUGIN_INTERVAL = 10
COLLECTD_CONF = '/etc/collectd.conf'
COLLECTD_CONF_DIR = '/etc/collectd/collectd.conf.d'
NOTIFICATION_FILE = '/var/log/python-notifications.dump'
COLLECTD_NOTIFICATION = '/etc/collectd_notification_dump.py'
APEX_IP = os.getenv("INSTALLER_IP").rstrip('\n')
APEX_USER = 'root'
APEX_USER_STACK = 'stack'
APEX_PKEY = '/root/.ssh/id_rsa'
TEST_VM_IMAGE = 'cirros-0.4.0-x86_64-disk.img'
TEST_VM_IMAGE_PATH = '/home/opnfv/functest/images/' + TEST_VM_IMAGE


class Node(object):
    """Node configuration class"""
    def __init__(self, attrs):
        self.__null = attrs[0]
        self.__id = attrs[1]
        self.__name = attrs[2]
        self.__status = attrs[3] if attrs[3] else None
        self.__taskState = attrs[4]
        self.__pwrState = attrs[5]
        self.__ip = re.sub('^[a-z]+=', '', attrs[6])

    def get_name(self):
        """Get node name"""
        return self.__name

    def get_id(self):
        """Get node ID"""
        return self.__id

    def get_ip(self):
        """Get node IP address"""
        return self.__ip

    def get_roles(self):
        """Get node role"""
        return self.__roles


def get_apex_nodes():
    handler = factory.Factory.get_handler('apex',
                                          APEX_IP,
                                          APEX_USER_STACK,
                                          APEX_PKEY)
    nodes = handler.get_nodes()
    return nodes


class ConfigServer(object):
    """Class to get env configuration"""
    def __init__(self, host, user, logger, priv_key=None):
        self.__host = host
        self.__user = user
        self.__passwd = None
        self.__priv_key = priv_key
        self.__nodes = list()
        self.__logger = logger

        self.__private_key_file = ID_RSA_PATH
        if not os.path.isfile(self.__private_key_file):
            self.__logger.error(
                "Private key file '{}'".format(self.__private_key_file)
                + " not found.")
            raise IOError("Private key file '{}' not found.".format(
                self.__private_key_file))

        # get list of available nodes
        ssh, sftp = self.__open_sftp_session(
            self.__host, self.__user, self.__passwd)
        attempt = 1
        fuel_node_passed = False

        while (attempt <= 10) and not fuel_node_passed:
            stdin, stdout, stderr = ssh.exec_command(
                "source stackrc; nova list")
            stderr_lines = stderr.readlines()
            if stderr_lines:
                self.__logger.warning(
                    "'Apex node' command failed (try {}):".format(attempt))
                for line in stderr_lines:
                    self.__logger.debug(line.strip())
            else:
                fuel_node_passed = True
                if attempt > 1:
                    self.__logger.info(
                        "'Apex node' command passed (try {})".format(attempt))
            attempt += 1
        if not fuel_node_passed:
            self.__logger.error(
                "'Apex node' command failed. This was the last try.")
            raise OSError(
                "'Apex node' command failed. This was the last try.")
        node_table = stdout.readlines()\

        # skip table title and parse table values

        for entry in node_table[3:]:
            if entry[0] == '+' or entry[0] == '\n':
                print entry
                pass
            else:
                self.__nodes.append(
                    Node([str(x.strip(' \n')) for x in entry.split('|')]))

    def get_controllers(self):
        # Get list of controllers
        print self.__nodes[0]._Node__ip
        return (
            [node for node in self.__nodes if 'controller' in node.get_name()])

    def get_computes(self):
        # Get list of computes
        return (
            [node for node in self.__nodes if 'compute' in node.get_name()])

    def get_nodes(self):
        # Get list of nodes
        return self.__nodes

    def __open_sftp_session(self, host, user, passwd=None):
        # Connect to given host.
        """Keyword arguments:
        host -- host to connect
        user -- user to use
        passwd -- password to use

        Return tuple of SSH and SFTP client instances.
        """
        # create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # try a direct access using password or private key
        if not passwd and not self.__priv_key:
            # get private key
            self.__priv_key = paramiko.RSAKey.from_private_key_file(
                self.__private_key_file)

        # connect to the server
        ssh.connect(
            host, username=user, password=passwd, pkey=self.__priv_key)
        sftp = ssh.open_sftp()

        # return SFTP client instance
        return ssh, sftp

    def get_plugin_interval(self, compute, plugin):
        """Find the plugin interval in collectd configuration.

        Keyword arguments:
        compute -- compute node instance
        plugin -- plug-in name

        If found, return interval value, otherwise the default value"""
        default_interval = DEF_PLUGIN_INTERVAL
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd(
                    'cat /etc/collectd/collectd.conf.d/{}.conf'.format(plugin))
                if stdout is None:
                    return default_interval
                for line in stdout.split('\n'):
                    if 'Interval' in line:
                        return 1
        return default_interval

    def get_plugin_config_values(self, compute, plugin, parameter):
        """Get parameter values from collectd config file.

        Keyword arguments:
        compute -- compute node instance
        plugin -- plug-in name
        parameter -- plug-in parameter

        Return list of found values."""
        default_values = []
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd(
                    'cat /etc/collectd/collectd.conf.d/{}.conf' .format(plugin))
                if stdout is None:
                    return default_values
                for line in stdout.split('\n'):
                    if 'Interfaces' in line:
                        return line.split(' ', 1)[1]
                    elif 'Bridges' in line:
                        return line.split(' ', 1)[1]
                    elif 'Cores' in line:
                        return line.split(' ', 1)[1]
                    else:
                        pass
        return default_values

    def execute_command(self, command, host_ip=None, ssh=None):
        """Execute command on node and return list of lines of standard output.

        Keyword arguments:
        command -- command
        host_ip -- IP of the node
        ssh -- existing open SSH session to use

        One of host_ip or ssh must not be None. If both are not None,
        existing ssh session is used.
        """
        if host_ip is None and ssh is None:
            raise ValueError('One of host_ip or ssh must not be None.')
        if ssh is None:
            ssh, sftp = self.__open_sftp_session(host_ip, 'root', 'opnfvapex')
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.readlines()

    def get_ovs_interfaces(self, compute):
        """Get list of configured OVS interfaces

        Keyword arguments:
        compute -- compute node instance
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('sudo ovs-vsctl list-br')
        return stdout

    def is_gnocchi_running(self, controller):
        """Check whether Gnocchi is running on controller.

        Keyword arguments:
        controller -- controller node instance

        Return boolean value whether Gnocchi is running.
        """
        gnocchi_present = False
        controller_name = controller.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if controller_name == node.get_dict()['name']:
                node.put_file(constants.ENV_FILE, 'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "openstack catalog list | grep gnocchi")
                if stdout is None:
                    return False
                elif 'gnocchi' in stdout:
                    gnocchi_present = True
                    return gnocchi_present
                else:
                    return False
        return gnocchi_present

    def is_aodh_running(self, controller):
        """Check whether aodh service is running on controller
        """
        aodh_present = False
        controller_name = controller.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if controller_name == node.get_dict()['name']:
                node.put_file(constants.ENV_FILE, 'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "openstack catalog list | grep aodh")
                if stdout is None:
                    return False
                elif 'aodh' in stdout:
                    aodh_present = True
                    return aodh_present
                else:
                    return False
        return aodh_present

    def is_redis_running(self, compute):
        """Check whether redis service is running on compute"""
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('sudo systemctl status docker'
                                      '&& sudo docker ps'
                                      '| grep barometer-redis')
                if stdout and 'barometer-redis' in stdout:
                    self.__logger.info(
                        'Redis is running in node {}'.format(
                         compute_name))
                    return True
        self.__logger.info(
            'Redis is *not* running in node {}'.format(
             compute_name))
        return False

    def is_dma_server_running(self, compute):
        """Check whether DMA server is running on compute"""
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('sudo systemctl status docker'
                                      '&& sudo docker ps'
                                      '| grep opnfv/barometer-dma')
                if stdout and '/server' in stdout:
                    self.__logger.info(
                        'DMA Server is running in node {}'.format(
                         compute_name))
                    return True
        self.__logger.info(
            'DMA Server is *not* running in node {}'.format(
             compute_name))
        return False

    def is_dma_infofetch_running(self, compute):
        """Check whether DMA infofetch is running on compute"""
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('sudo systemctl status docker'
                                      '&& sudo docker ps'
                                      '| grep opnfv/barometer-dma')
                if stdout and '/infofetch' in stdout:
                    self.__logger.info(
                        'DMA InfoFetch is running in node {}'.format(
                         compute_name))
                    return True
        self.__logger.info(
            'DMA InfoFetch is *not* running in node {}'.format(
             compute_name))
        return False

    def get_dma_config(self, compute):
        """Get config values of DMA"""
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                # We use following after functest accept python-toml
                #     stdout = node.run_cmd(
                #         'cat /etc/barometer-dma/config.toml')
                #     try:
                #         agent_conf = toml.loads(stdout)
                #     except (TypeError, TomlDecodeError) as e:
                #         self.__logger.error(
                #             'DMA config error: {}'.format(e))
                #         agent_conf = None
                #     finally:
                #         return agent_conf
                readcmd = (
                    'egrep "listen_port|amqp_"'
                    ' /etc/barometer-dma/config.toml'
                    '| sed -e "s/#.*$//" | sed -e "s/=/:/"'
                    )
                stdout = node.run_cmd(readcmd)
                agent_conf = {"server": yaml.safe_load(stdout)}

                pingcmd = (
                    'ping -n -c1 ' + agent_conf["server"]["amqp_host"] +
                    '| sed -ne "s/^.*bytes from //p" | sed -e "s/:.*//"'
                    )
                agent_conf["server"]["amqp_host"] = node.run_cmd(pingcmd)

                return agent_conf
        return None

    def is_mcelog_installed(self, compute, package):
        """Check whether package exists on compute node.

        Keyword arguments:
        compute -- compute node instance
        package -- Linux package to search for

        Return boolean value whether package is installed.
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd(
                    'rpm -qa | grep mcelog')
                if stdout is None:
                    return 0
                elif 'mcelog' in stdout:
                    return 1
                else:
                    return 0

    def is_rdt_available(self, compute):
        """Check whether the compute node is a virtual machine."""
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('cat /proc/cpuinfo | grep hypervisor')
                if 'hypervisor' in stdout:
                    return False
        return True

    def is_libpqos_on_node(self, compute):
        """Check whether libpqos is present on compute node"""

        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd('ls /usr/local/lib/ | grep libpqos')
                if 'libpqos' in stdout:
                    return True
        return False

    def check_aodh_plugin_included(self, compute):
        """Check if aodh plugin is included in collectd.conf file.
        If not, try to enable it.

        Keyword arguments:
        compute -- compute node instance

        Return boolean value whether AODH plugin is included
        or it's enabling was successful.
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                aodh_conf = node.run_cmd('ls /etc/collectd/collectd.conf.d')
                if 'aodh.conf' not in aodh_conf:
                    self.__logger.info(
                        "AODH Plugin not included in {}".format(compute_name))
                    return False
                else:
                    self.__logger.info(
                        "AODH plugin present in compute node {}" .format(
                            compute_name))
                    return True
        return True

    def check_gnocchi_plugin_included(self, compute):
        """Check if gnocchi plugin is included in collectd.conf file.
        If not, try to enable it.

        Keyword arguments:
        compute -- compute node instance

        Return boolean value whether gnocchi plugin is included
        or it's enabling was successful.
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                gnocchi_conf = node.run_cmd('ls /etc/collectd/collectd.conf.d')
                if 'collectd-ceilometer-plugin.conf' not in gnocchi_conf:
                    self.__logger.info(
                        "Gnocchi Plugin not included in node {}".format(
                            compute_name))
                    return False
                else:
                    self.__logger.info(
                        "Gnocchi plugin available in compute node {}" .format(
                            compute_name))
                    return True
        return True

    def check_snmp_plugin_included(self, compute):
        """Check if SNMP plugin is active in compute node.
        """
        snmp_mib = '/usr/share/snmp/mibs/Intel-Rdt.txt'
        snmp_string = 'INTEL-RDT-MIB::intelRdt'
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd(
                    'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                        snmp_mib, snmp_string))
                self.__logger.info("snmp output = {}" .format(stdout))
                if 'OID' in stdout:
                    return False
                else:
                    return True

    def enable_plugins(
            self, compute, plugins, error_plugins, create_backup=True):
        """Enable plugins on compute node

        Keyword arguments:
        compute -- compute node instance
        plugins -- list of plugins to be enabled

        Return boolean value indicating whether function was successful.
        """
        csv_file = os.path.dirname(os.path.realpath(__file__)) + '/csv.conf'
        plugins = sorted(plugins)
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                node.put_file(csv_file, 'csv.conf')
                node.run_cmd(
                    'sudo cp csv.conf '
                    + '/etc/collectd/collectd.conf.d/csv.conf')
        return True

    def restart_collectd(self, compute):
        """Restart collectd on compute node.

        Keyword arguments:
        compute -- compute node instance

        Retrun tuple with boolean indicating success and list of warnings
        received during collectd start.
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()

        def get_collectd_processes(compute_node):
            """Get number of running collectd processes.

            Keyword arguments:
            ssh_session -- instance of SSH session in which to check
                for processes
            """
            stdout = compute_node.run_cmd("pgrep collectd")
            return len(stdout)

        for node in nodes:
            if compute_name == node.get_dict()['name']:
                # node.run_cmd('su; "opnfvapex"')
                self.__logger.info('Stopping collectd service...')
                node.run_cmd('sudo systemctl stop collectd')
                time.sleep(10)
                if get_collectd_processes(node):
                    self.__logger.error('Collectd is still running...')
                    return False, []
                self.__logger.info('Starting collectd service...')
                stdout = node.run_cmd('sudo systemctl start collectd')
                time.sleep(10)
                warning = [
                    output.strip() for output in stdout if 'WARN: ' in output]
                if get_collectd_processes(node) == 0:
                    self.__logger.error('Collectd is still not running...')
                    return False, warning
        return True, warning

    def trigger_alarm_update(self, alarm, compute_node):
        # TODO: move these actions to main, with criteria lists so that we can reference that
        # i.e. test_plugin_with_aodh(self, compute, plugin.., logger, criteria_list, alarm_action)
        if alarm == 'mcelog':
            compute_node.run_cmd('sudo modprobe mce-inject')
            compute_node.run_cmd('sudo ./mce-inject_ea < corrected')
        if alarm == 'ovs_events':
            compute_node.run_cmd('sudo ifconfig -a | grep br0')
            compute_node.run_cmd('sudo ifconfig br0 down; sudo ifconfig br0 up')

    def test_plugins_with_aodh(
            self, compute, plugin_interval, logger,
            criteria_list=[]):

        metric_id = {}
        timestamps1 = {}
        timestamps2 = {}
        nodes = get_apex_nodes()
        compute_node = [node for node in nodes if node.get_dict()['name'] == compute][0]
        for node in nodes:
            if node.is_controller():
                self.__logger.info('Getting AODH Alarm list on {}' .format(
                    (node.get_dict()['name'])))
                node.put_file(constants.ENV_FILE, 'overcloudrc.v3')
                self.trigger_alarm_update(criteria_list, compute_node)
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "aodh alarm list | grep {0} | grep {1}"
                    .format(criteria_list, compute))
                if stdout is None:
                    self.__logger.info("aodh alarm list was empty")
                    return False
                for line in stdout.splitlines():
                    line = line.replace('|', "")
                    metric_id = line.split()[0]
                    stdout = node.run_cmd(
                        'source overcloudrc.v3; aodh alarm show {}' .format(
                            metric_id))
                    if stdout is None:
                        self.__logger.info("aodh alarm list was empty")
                        return False
                    for line in stdout.splitlines()[3: -1]:
                        line = line.replace('|', "")
                        if line.split()[0] == 'state_timestamp':
                            timestamps1 = line.split()[1]
                    self.trigger_alarm_update(criteria_list, compute_node)
                    time.sleep(12)
                    stdout = node.run_cmd(
                        "source overcloudrc.v3; aodh alarm show {}" .format(
                            metric_id))
                    if stdout is None:
                        self.__logger.info("aodh alarm list was empty")
                        return False
                    for line in stdout.splitlines()[3:-1]:
                        line = line.replace('|', "")
                        if line.split()[0] == 'state_timestamp':
                            timestamps2 = line.split()[1]
                    if timestamps1 == timestamps2:
                        self.__logger.info(
                            "Data not updated after interval of 12 seconds")
                        return False
                    else:
                        self.__logger.info("PASS")
                        return True

    def test_plugins_with_gnocchi(
            self, compute, plugin_interval, logger,
            criteria_list=[]):

        metric_id = {}
        timestamps1 = {}
        timestamps2 = {}
        nodes = get_apex_nodes()
        if plugin_interval > 15:
            sleep_time = plugin_interval*2
        else:
            sleep_time = 30

        for node in nodes:
            if node.is_controller():
                self.__logger.info('Getting gnocchi metric list on {}' .format(
                    (node.get_dict()['name'])))
                node.put_file(constants.ENV_FILE, 'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "gnocchi metric list | grep {0} | grep {1}"
                    .format(criteria_list, compute))
                if stdout is None:
                        self.__logger.info("gnocchi list was empty")
                        return False
                for line in stdout.splitlines():
                    line = line.replace('|', "")
                    metric_id = line.split()[0]
                    stdout = node.run_cmd(
                        'source overcloudrc.v3;gnocchi measures show {}'.format(
                            metric_id))
                    if stdout is None:
                        self.__logger.info("gnocchi list was empty")
                        return False
                    for line in stdout.splitlines()[3: -1]:
                        if line[0] == '+':
                            pass
                        else:
                            timestamps1 = line.replace('|', "")
                            timestamps1 = timestamps1.split()[0]
                    time.sleep(sleep_time)
                    stdout = node.run_cmd(
                        "source overcloudrc.v3;gnocchi measures show {}".format(
                            metric_id))
                    if stdout is None:
                        self.__logger.info("gnocchi measures was empty")
                        return False
                    for line in stdout.splitlines()[3:-1]:
                        if line[0] == '+':
                            pass
                        else:
                            timestamps2 = line.replace('|', "")
                            timestamps2 = timestamps2.split()[0]
                    if timestamps1 == timestamps2:
                        self.__logger.info(
                            "Plugin Interval is {}" .format(plugin_interval))
                        self.__logger.info(
                            "Data not updated after {} seconds".format(
                                sleep_time))
                        return False
                    else:
                        self.__logger.info("PASS")
                        return True
        return False

    def test_plugins_with_snmp(
            self, compute, plugin_interval, logger, plugin, snmp_mib_files=[],
            snmp_mib_strings=[], snmp_in_commands=[]):

        if plugin in ('hugepages', 'intel_rdt', 'mcelog'):
            nodes = get_apex_nodes()
            for node in nodes:
                if compute == node.get_dict()['name']:
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if stdout is None:
                        self.__logger.info("No output from snmpwalk")
                        return False
                    elif 'OID' in stdout:
                        self.__logger.info("SNMP query failed")
                        return False
                    else:
                        counter1 = stdout.split()[3]
                    time.sleep(10)
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if stdout is None:
                        self.__logger.info("No output from snmpwalk")
                    elif 'OID' in stdout:
                        self.__logger.info(
                            "SNMP query failed during second check")
                        self.__logger.info("waiting for 10 sec")
                        time.sleep(10)
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if stdout is None:
                        self.__logger.info("No output from snmpwalk")
                    elif 'OID' in stdout:
                        self.__logger.info("SNMP query failed again")
                        self.__logger.info("Failing this test case")
                        return False
                    else:
                        counter2 = stdout.split()[3]

                    if counter1 == counter2:
                        return False
                    else:
                        return True
        else:
            return False

    def check_dma_dummy_included(self, compute, name):
        """Check if dummy collectd config by DMA
           is included in collectd.conf file.

        Keyword arguments:
        compute -- compute node instance
        name -- config file name
        """
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                dummy_conf = node.run_cmd('ls /etc/collectd/collectd.conf.d')
                if name + '.conf' not in dummy_conf:
                    self.__logger.error('check conf FAIL')
                    return False
                else:
                    self.__logger.info('check conf PASS')
                    fullpath = '/etc/collectd/collectd.conf.d/{}'.format(
                               name + '.conf')
                    self.__logger.info('Delete file {}'.format(fullpath))
                    node.run_cmd('sudo rm -f ' + fullpath)
                    return True
        self.__logger.error('Some panic, compute not found')
        return False

    def create_testvm(self, compute_node, test_name):
        nodes = get_apex_nodes()
        compute_name = compute_node.get_name()

        controller_node = None
        for node in nodes:
            if node.is_controller():
                controller_node = node
                break

        self.__logger.debug('Creating Test VM on {}' .format(compute_name))
        self.__logger.debug('Create command is executed in {}' .format(
            (controller_node.get_dict()['name'])))

        node.put_file(constants.ENV_FILE, 'overcloudrc.v3')
        node.put_file(TEST_VM_IMAGE_PATH, TEST_VM_IMAGE)
        image = controller_node.run_cmd(
            'source overcloudrc.v3;'
            'openstack image create -f value -c id'
            ' --disk-format qcow2 --file {0} {1}'
            .format(TEST_VM_IMAGE, test_name))
        flavor = controller_node.run_cmd(
            'source overcloudrc.v3;'
            'openstack flavor create -f value -c id {}'
            .format(test_name))
        host = controller_node.run_cmd(
            'source overcloudrc.v3;'
            'openstack hypervisor list -f value -c "Hypervisor Hostname"'
            ' | grep "^{}\\."'
            .format(compute_name))
        server = controller_node.run_cmd(
            'source overcloudrc.v3;'
            'openstack server create -f value -c id'
            ' --image {0} --flavor {1} --availability-zone {2} {3}'
            .format(image, flavor, 'nova:' + host, test_name))

        resources = {"image": image, "flavor": flavor, "server": server}

        if server:
            self.__logger.debug('VM created')
        self.__logger.debug('VM info: {}'.format(resources))

        return resources

    def delete_testvm(self, resources):
        nodes = get_apex_nodes()

        controller_node = None
        for node in nodes:
            if node.is_controller():
                controller_node = node
                break

        self.__logger.debug('Deleteing Test VM')
        self.__logger.debug('VM to be deleted info: {}'.format(resources))
        self.__logger.debug('Delete command is executed in {}' .format(
            (controller_node.get_dict()['name'])))

        server = resources.get('server', None)
        flavor = resources.get('flavor', None)
        image = resources.get('image', None)
        if server:
            controller_node.run_cmd(
                'source overcloudrc.v3;'
                'openstack server delete {}'.format(server))
        if flavor:
            controller_node.run_cmd(
                'source overcloudrc.v3;'
                'openstack flavor delete {}'.format(flavor))
        if image:
            controller_node.run_cmd(
                'source overcloudrc.v3;'
                'openstack image delete {}'.format(image))

        self.__logger.debug('VM and other OpenStack resources deleted')

    def test_dma_infofetch_get_data(self, compute, test_name):
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                stdout = node.run_cmd(
                    'redis-cli keys "barometer-dma/vm/*/vminfo"'
                    ' | while read k; do redis-cli get $k; done'
                    ' | grep {}'.format(test_name))
                self.__logger.debug('InfoFetch data: {}'.format(stdout))
                if stdout and test_name in stdout:
                    self.__logger.info('PASS')
                    return True
                else:
                    self.__logger.info('No test vm info')

        self.__logger.info('FAIL')
        return False
