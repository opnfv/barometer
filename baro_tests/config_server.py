# -*- coding: utf-8 -*-
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

"""Classes used by collectd.py"""

import paramiko
import time
import os.path
import os
import re
import subprocess
from opnfv.deployment import factory
ID_RSA_PATH = '/root/.ssh/id_rsa'
SSH_KEYS_SCRIPT = '/home/opnfv/barometer/baro_utils/get_ssh_keys.sh'
DEF_PLUGIN_INTERVAL = 10
COLLECTD_CONF = '/etc/collectd.conf'
COLLECTD_CONF_DIR = '/etc/collectd/collectd.conf.d'
NOTIFICATION_FILE = '/var/log/python-notifications.dump'
COLLECTD_NOTIFICATION = '/etc/collectd_notification_dump.py'
APEX_IP = subprocess.check_output("echo $INSTALLER_IP", shell=True)
APEX_USER = 'root'
APEX_USER_STACK = 'stack'
APEX_PKEY = '/root/.ssh/id_rsa'


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
                    "'fuel node' command failed (try {}):".format(attempt))
                for line in stderr_lines:
                    self.__logger.debug(line.strip())
            else:
                fuel_node_passed = True
                if attempt > 1:
                    self.__logger.info(
                        "'fuel node' command passed (try {})".format(attempt))
            attempt += 1
        if not fuel_node_passed:
            self.__logger.error(
                "'fuel node' command failed. This was the last try.")
            raise OSError(
                "'fuel node' command failed. This was the last try.")
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
                for line in stdout.split('\n'):
                    if 'Interval' in line:
                        # line = line.strip('Interval')
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
                node.put_file(
                    '/home/opnfv/functest/conf/openstack.creds',
                    'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "openstack catalog list | grep gnocchi")
                if 'gnocchi' in stdout:
                    gnocchi_present = True
        return gnocchi_present

    def is_aodh_running(self, controller):
        """Check whether aodh service is running on controller
        """
        aodh_present = False
        controller_name = controller.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if controller_name == node.get_dict()['name']:
                node.put_file(
                    '/home/opnfv/functest/conf/openstack.creds',
                    'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "openstack catalog list | grep aodh")
                if 'aodh' in stdout:
                    aodh_present = True
        return aodh_present

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
                    'yum list installed | grep mcelog')
                if 'mcelog' in stdout:
                    return 1
                else:
                    return 0

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
                        "AODH Plugin not included in compute node")
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
                    self.__logger.info("Gnocchi Plugin not included")
                    return False
                else:
                    self.__logger.info(
                        "Gnochi plugin available in compute node {}" .format(
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
        plugins = sorted(plugins)
        compute_name = compute.get_name()
        nodes = get_apex_nodes()
        for node in nodes:
            if compute_name == node.get_dict()['name']:
                node.put_file(
                    '/usr/local/lib/python2.7/dist-packages/baro_tests/'
                    + 'csv.conf', 'csv.conf')
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

    def test_plugins_with_aodh(
            self, compute, plugin_interval, logger,
            criteria_list=[]):

        metric_id = {}
        timestamps1 = {}
        timestamps2 = {}
        nodes = get_apex_nodes()
        for node in nodes:
            if node.is_controller():
                self.__logger.info('Getting AODH Alarm list on {}' .format(
                    (node.get_dict()['name'])))
                node.put_file(
                    '/home/opnfv/functest/conf/openstack.creds',
                    'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "aodh alarm list | grep {0} | grep {1}"
                    .format(criteria_list, compute))
                for line in stdout.splitlines():
                    line = line.replace('|', "")
                    metric_id = line.split()[0]
                    stdout = node.run_cmd(
                        'source overcloudrc.v3; aodh alarm show {}' .format(
                            metric_id))
                    for line in stdout.splitlines()[3: -1]:
                        line = line.replace('|', "")
                        if line.split()[0] == 'timestamp':
                            timestamps1 = line.split()[1]
                        else:
                            pass
                    time.sleep(12)
                    stdout = node.run_cmd(
                        "source overcloudrc.v3; aodh alarm show {}" .format(
                            metric_id))
                    for line in stdout.splitlines()[3:-1]:
                        line = line.replace('|', "")
                        if line.split()[0] == 'timestamp':
                            timestamps2 = line.split()[1]
                        else:
                            pass
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
        for node in nodes:
            if node.is_controller():
                self.__logger.info('Getting gnocchi metric list on {}' .format(
                    (node.get_dict()['name'])))
                node.put_file(
                    '/home/opnfv/functest/conf/openstack.creds',
                    'overcloudrc.v3')
                stdout = node.run_cmd(
                    "source overcloudrc.v3;"
                    + "gnocchi metric list | grep {0} | grep {1}"
                    .format(criteria_list, compute))
                for line in stdout.splitlines():
                    line = line.replace('|', "")
                    metric_id = line.split()[0]
                    stdout = node.run_cmd(
                        'source overcloudrc.v3;gnocchi measures show {}'.format(
                            metric_id))
                    for line in stdout.splitlines()[3: -1]:
                        if line[0] == '+':
                            pass
                        else:
                            timestamps1 = line.replace('|', "")
                            timestamps1 = timestamps1.split()[0]
                    time.sleep(10)
                    stdout = node.run_cmd(
                        "source overcloudrc.v3;gnocchi measures show {}".format(
                            metric_id))
                    for line in stdout.splitlines()[3:-1]:
                        if line[0] == '+':
                            pass
                        else:
                            timestamps2 = line.replace('|', "")
                            timestamps2 = timestamps2.split()[0]
                    if timestamps1 == timestamps2:
                        self.__logger.info("Data not updated after 12 seconds")
                        return False
                    else:
                        self.__logger.info("PASS")
                        return True

    def test_plugins_with_snmp(
            self, compute, plugin_interval, logger, plugin, snmp_mib_files=[],
            snmp_mib_strings=[], snmp_in_commands=[]):

        if plugin == 'intel_rdt':
            nodes = get_apex_nodes()
            for node in nodes:
                if compute == node.get_dict()['name']:
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if 'OID' in stdout:
                        self.__logger.info("SNMP query failed")
                        return False
                    else:
                        counter1 = stdout.split()[3]
                    time.sleep(10)
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if 'OID' in stdout:
                        self.__logger.info(
                            "SNMP query failed during second check")
                        self.__logger.info("waiting for 10 sec")
                        time.sleep(10)
                    stdout = node.run_cmd(
                        'snmpwalk -v2c -m {0} -c public localhost {1}' .format(
                            snmp_mib_files, snmp_mib_strings))
                    self.__logger.info("{}" .format(stdout))
                    if 'OID' in stdout:
                        self.__logger.info("SNMP query failed again")
                        self.__logger.info("Failing this test case")
                        return False
                    else:
                        counter2 = stdout.split()[3]

                    if counter1 == counter2:
                        return False
                    else:
                        return True
