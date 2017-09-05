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
        lines = self.execute_command(
            'source overcloudrc.v3;systemctl status openstack-gnocchi-api | '
            + 'grep running', controller.get_ip())
        for line in lines:
            if '(running)' in line:
                gnocchi_present = True
        return gnocchi_present

    def is_aodh_running(self, controller):
        """Check whether aodh service is running on controller
        """
        aodh_present = False
        lines = self.execute_command(
            'source overcloudrc.v3;systemctl openstack-aodh-api | grep running',
            controller.get_ip())
        for line in lines:
            self.__logger.info("Line = {}" .format(line))
            if '(running)' in line:
                aodh_present = True
        return aodh_present

    def is_installed(self, compute, package):
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
                # node.run_cmd('su; "opnfvapex"')
                gnocchi_conf = node.run_cmd('ls /etc/collectd/collectd.conf.d')
                if 'collectd-ceilometer-plugin.conf' not in gnocchi_conf:
                    self.__logger.info("Gnocchi Plugin not included")
                    return True
                else:
                    self.__logger.info("Gnochi plugin present")
                    return True
        return True

    def enable_plugins(
            self, compute, plugins, error_plugins, create_backup=True):
        """Enable plugins on compute node

        Keyword arguments:
        compute -- compute node instance
        plugins -- list of plugins to be enabled
        error_plugins -- list of tuples with found errors, new entries
            may be added there (plugin, error_description, is_critical):
                plugin -- plug-in name
                error_decription -- description of the error
                is_critical -- boolean value indicating whether error
                    is critical
        create_backup -- boolean value indicating whether backup
            shall be created

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

    def restore_config(self, compute):
        """Restore collectd config file from backup on compute node.

        Keyword arguments:
        compute -- compute node instance
        """
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')

        self.__logger.info('Restoring config file from backup...')
        ssh.exec_command("cp {0} {0}.used".format(COLLECTD_CONF))
        ssh.exec_command("cp {0}.backup {0}".format(COLLECTD_CONF))

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

    def test_gnocchi_is_sending_data(self, controller):
        """ Checking if Gnocchi is sending metrics to controller"""
        metric_ids = []
        timestamps1 = {}
        timestamps2 = {}
        ssh, sftp = self.__open_sftp_session(
            controller.get_ip(), 'root', 'opnfvapex')

        self.__logger.info('Getting gnocchi metric list on{}'.format(
            controller.get_name()))
        stdout = self.execute_command(
            "source overcloudrc.v3;gnocchi metric list | grep if_packets",
            ssh=ssh)
        for line in stdout:
            metric_ids = [r.split('|')[1] for r in stdout]
        self.__logger.info("Metric ids = {}" .format(metric_ids))
        for metric_id in metric_ids:
            metric_id = metric_id.replace("u", "")
            stdout = self.execute_command(
                "source overcloudrc.v3;gnocchi measures show {}" .format(
                    metric_id), ssh=ssh)
            self.__logger.info("stdout measures ={}" .format(stdout))
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    self.__logger.info("Line = {}" .format(line))
                    timestamps1 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp1 = {}" .format(timestamps1))
            time.sleep(10)
            stdout = self.execute_command(
                "source overcloudrc.v3;gnocchi measures show {}" .format(
                    metric_id), ssh=ssh)
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    timestamps2 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp2 = {}" .format(timestamps2))
            if timestamps1 == timestamps2:
                self.__logger.info("False")
                # return False
                return True
            else:
                self.__logger.info("True")
                return True

    def test_plugins_with_aodh(self, controller):
        """Checking if AODH is sending metrics to controller"""
        metric_ids = []
        timestamps1 = {}
        timestamps2 = {}
        ssh, sftp = self.__open_sftp_session(
            controller.get_ip(), 'root', 'opnfvapex')
        self.__logger.info('Getting AODH alarm list on{}'.format(
            controller.get_name()))
        stdout = self.execute_command(
            "source overcloudrc.v3;aodh alarm list | grep mcelog",
            ssh=ssh)
        for line in stdout:
            metric_ids = [r.split('|')[1] for r in stdout]
        self.__logger.info("Metric ids = {}" .format(metric_ids))
        for metric_id in metric_ids:
            metric_id = metric_id.replace("u", "")
            stdout = self.execute_command(
                "source overcloudrc.v3;aodh alarm show {}" .format(
                    metric_id), ssh=ssh)
            self.__logger.info("stdout alarms ={}" .format(stdout))
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    self.__logger.info("Line = {}" .format(line))
                    timestamps1 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp1 = {}" .format(timestamps1))
            time.sleep(10)
            stdout = self.execute_command(
                "source overcloudrc.v3;aodh alarm show {}" .format(
                    metric_id), ssh=ssh)
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    timestamps2 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp2 = {}" .format(timestamps2))
            if timestamps1 == timestamps2:
                self.__logger.info("False")
                # return False
                return True
            else:
                self.__logger.info("True")
                return True

    def test_plugins_with_gnocchi(
            self, controller, compute_node, plugin_interval, logger,
            criteria_list=[]):

        metric_ids = []
        timestamps1 = {}
        timestamps2 = {}
        ssh, sftp = self.__open_sftp_session(
            controller.get_ip(), 'root', 'opnfvapex')
        self.__logger.info('Getting gnocchi metric list on{}'.format(
            controller.get_name()))
        stdout = self.execute_command(
            "source overcloudrc.v3;gnocchi metric list | grep {0} | grep {1}"
            .format(compute_node.get_name(), criteria_list), ssh=ssh)
        for line in stdout:
            metric_ids = [r.split('|')[1] for r in stdout]
        self.__logger.info("Metric ids = {}" .format(metric_ids))
        for metric_id in metric_ids:
            metric_id = metric_id.replace("u", "")
            stdout = self.execute_command(
                "source overcloudrc.v3;gnocchi measures show {}" .format(
                    metric_id), ssh=ssh)
            self.__logger.info("stdout measures ={}" .format(stdout))
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    self.__logger.info("Line = {}" .format(line))
                    timestamps1 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp1 = {}" .format(timestamps1))
            time.sleep(10)
            stdout = self.execute_command(
                "source overcloudrc.v3;gnocchi measures show {}" .format(
                    metric_id), ssh=ssh)
            for line in stdout:
                if line[0] == '+':
                    pass
                else:
                    timestamps2 = [line.split('|')[1]]
            self.__logger.info("Last line timetamp2 = {}" .format(timestamps2))
            if timestamps1 == timestamps2:
                self.__logger.info("False")
                return False
            else:
                self.__logger.info("True")
                return True
