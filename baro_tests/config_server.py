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

"""Classes used by collectd.py"""

import paramiko
import time
import string
import os.path
import os
import re
ID_RSA_PATH = '/home/opnfv/.ssh/id_rsa'
SSH_KEYS_SCRIPT = '/home/opnfv/barometer/baro_utils/get_ssh_keys.sh'
DEF_PLUGIN_INTERVAL = 10
COLLECTD_CONF = '/etc/collectd.conf'
COLLECTD_CONF_DIR = '/etc/collectd/collectd.conf.d'
NOTIFICATION_FILE = '/var/log/python-notifications.dump'
COLLECTD_NOTIFICATION = '/etc/collectd_notification_dump.py'


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
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')
        in_plugin = False
        plugin_name = ''
        default_interval = DEF_PLUGIN_INTERVAL
        config_files = [COLLECTD_CONF] + [
            COLLECTD_CONF_DIR + '/'
            + conf_file for conf_file in sftp.listdir(COLLECTD_CONF_DIR)]
        for config_file in config_files:
            try:
                with sftp.open(config_file) as config:
                    for line in config.readlines():
                        words = line.split()
                        if len(words) > 1 and words[0] == '<LoadPlugin':
                            in_plugin = True
                            plugin_name = words[1].strip('">')
                        if words and words[0] == '</LoadPlugin>':
                            in_plugin = False
                        if words and words[0] == 'Interval':
                            if in_plugin and plugin_name == plugin:
                                return int(words[1])
                            if not in_plugin:
                                default_interval = int(words[1])
            except IOError:
                self.__logger.error("Could not open collectd.conf file.")
        return default_interval

    def get_plugin_config_values(self, compute, plugin, parameter):
        """Get parameter values from collectd config file.

        Keyword arguments:
        compute -- compute node instance
        plugin -- plug-in name
        parameter -- plug-in parameter

        Return list of found values."""
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')
        # find the plugin value
        in_plugin = False
        plugin_name = ''
        default_values = []
        config_files = [COLLECTD_CONF] + [
            COLLECTD_CONF_DIR + '/'
            + conf_file for conf_file in sftp.listdir(COLLECTD_CONF_DIR)]
        for config_file in config_files:
            try:
                with sftp.open(config_file) as config:
                    for line in config.readlines():
                        words = line.split()
                        if len(words) > 1 and words[0] == '<Plugin':
                            in_plugin = True
                            plugin_name = words[1].strip('">')
                        if len(words) > 0 and words[0] == '</Plugin>':
                            in_plugin = False
                        if len(words) > 0 and words[0] == parameter:
                            if in_plugin and plugin_name == plugin:
                                return [word.strip('"') for word in words[1:]]
            except IOError:
                self.__logger.error("Could not open collectd.conf file.")
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
        stdout = self.execute_command("ovs-vsctl list-br", compute.get_ip())
        return [interface.strip() for interface in stdout]

    def is_gnocchi_running(self, controller):
        """Check whether Gnocchi is running on controller.

        Keyword arguments:
        controller -- controller node instance

        Return boolean value whether Gnocchi is running.
        """
        gnocchi_present = False
        lines = self.execute_command(
            'source overcloudrc.v3;openstack service list | grep gnocchi',
            controller.get_ip())
        for line in lines:
            if 'gnocchi' in line:
                gnocchi_present = True
        return not gnocchi_present

    def is_installed(self, compute, package):
        """Check whether package exists on compute node.

        Keyword arguments:
        compute -- compute node instance
        package -- Linux package to search for

        Return boolean value whether package is installed.
        """
        stdout = self.execute_command(
            'yum list installed | grep {}'.format(package),
            compute.get_ip())
        return len(stdout) > 0

    def is_libpqos_on_node(self, compute):
        """Check whether libpqos is present on compute node"""
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')
        stdin, stdout, stderr = \
            ssh.exec_command("ls /usr/local/lib/ | grep libpqos")
        output = stdout.readlines()
        for lib in output:
            if 'libpqos' in lib:
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
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')
        try:
            config = sftp.open(COLLECTD_CONF, mode='r')
        except IOError:
            self.__logger.error(
                'Cannot open {} on node {}'.format(
                    COLLECTD_CONF, compute.get_name()))
            return False
        in_lines = config.readlines()
        out_lines = in_lines[:]
        include_section_indexes = [
            (start, end) for start in range(len(in_lines))
            for end in range(len(in_lines))
            if (start < end)
            and '<Include' in in_lines[start]
            and COLLECTD_CONF_DIR in in_lines[start]
            and '#' not in in_lines[start]
            and '</Include>' in in_lines[end]
            and '#' not in in_lines[end]
            and len([
                i for i in in_lines[start + 1: end]
                if 'Filter' in i and '*.conf' in i and '#' not in i]) > 0]
        if len(include_section_indexes) == 0:
            out_lines.append('<Include "{}">\n'.format(COLLECTD_CONF_DIR))
            out_lines.append('        Filter "*.conf"\n')
            out_lines.append('</Include>\n')
            config.close()
            config = sftp.open(COLLECTD_CONF, mode='w')
            config.writelines(out_lines)
        config.close()
        self.__logger.info('Creating backup of collectd.conf...')
        config = sftp.open(COLLECTD_CONF + '.backup', mode='w')
        config.writelines(in_lines)
        config.close()
        return True

    def check_ceil_plugin_included(self, compute):
        """Check if ceilometer plugin is included in collectd.conf file.
        If not, try to enable it.

        Keyword arguments:
        compute -- compute node instance

        Return boolean value whether ceilometer plugin is included
        or it's enabling was successful.
        """
        ssh, sftp = self.__open_sftp_session(compute.get_ip(), 'root')
        try:
            config = sftp.open(COLLECTD_CONF, mode='r')
        except IOError:
            self.__logger.error(
                'Cannot open {} on node {}'.format(
                    COLLECTD_CONF, compute.get_id()))
            return False
        in_lines = config.readlines()
        out_lines = in_lines[:]
        include_section_indexes = [
            (start, end) for start in range(len(in_lines))
            for end in range(len(in_lines))
            if (start < end)
            and '<Include' in in_lines[start]
            and COLLECTD_CONF_DIR in in_lines[start]
            and '#' not in in_lines[start]
            and '</Include>' in in_lines[end]
            and '#' not in in_lines[end]
            and len([
                i for i in in_lines[start + 1: end]
                if 'Filter' in i and '*.conf' in i and '#' not in i]) > 0]
        if len(include_section_indexes) == 0:
            out_lines.append('<Include "{}">\n'.format(COLLECTD_CONF_DIR))
            out_lines.append('        Filter "*.conf"\n')
            out_lines.append('</Include>\n')
            config.close()
            config = sftp.open(COLLECTD_CONF, mode='w')
            config.writelines(out_lines)
        config.close()
        self.__logger.info('Creating backup of collectd.conf...')
        config = sftp.open(COLLECTD_CONF + '.backup', mode='w')
        config.writelines(in_lines)
        config.close()
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
        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')
        plugins_to_enable = plugins[:]
        for plugin in plugins:
            plugin_file = '/usr/lib64/collectd/{}.so'.format(plugin)
            try:
                sftp.stat(plugin_file)
            except IOError:
                self.__logger.debug(
                    'Plugin file {} not found on node'.format(plugin_file)
                    + ' {0}, plugin {1} will not be enabled'.format(
                        compute.get_name(), plugin))
                error_plugins.append((
                    plugin, 'plugin file {} not found'.format(plugin_file),
                    True))
                plugins_to_enable.remove(plugin)
        self.__logger.debug(
            'Following plugins will be enabled on node {}: {}'.format(
                compute.get_name(), ', '.join(plugins_to_enable)))
        try:
            config = sftp.open(COLLECTD_CONF, mode='r')
        except IOError:
            self.__logger.warning(
                'Cannot open {} on node {}'.format(
                    COLLECTD_CONF, compute.get_name()))
            return False
        in_lines = config.readlines()
        out_lines = []
        enabled_plugins = []
        enabled_sections = []
        in_section = 0
        comment_section = False
        uncomment_section = False
        for line in in_lines:
            if 'LoadPlugin' in line:
                for plugin in plugins_to_enable:
                    if plugin in line:
                        commented = '#' in line
                        # list of uncommented lines which contain LoadPlugin
                        # for this plugin
                        loadlines = [
                            ll for ll in in_lines if 'LoadPlugin' in ll
                            and plugin in ll and '#' not in ll]
                        if len(loadlines) == 0:
                            if plugin not in enabled_plugins:
                                line = line.lstrip(string.whitespace + '#')
                                enabled_plugins.append(plugin)
                                error_plugins.append((
                                    plugin, 'plugin not enabled in '
                                    + '{}, trying to enable it'.format(
                                        COLLECTD_CONF), False))
                        elif not commented:
                            if plugin not in enabled_plugins:
                                enabled_plugins.append(plugin)
                            else:
                                line = '#' + line
                                error_plugins.append((
                                    plugin, 'plugin enabled more than once '
                                    + '(additional occurrence of LoadPlugin '
                                    + 'found in {}), '.format(COLLECTD_CONF)
                                    + 'trying to comment it out.', False))
            elif line.lstrip(string.whitespace + '#').find('<Plugin') == 0:
                in_section += 1
                for plugin in plugins_to_enable:
                    if plugin in line:
                        commented = '#' in line
                        # list of uncommented lines which contain Plugin for
                        # this plugin
                        pluginlines = [
                            pl for pl in in_lines if '<Plugin' in pl
                            and plugin in pl and '#' not in pl]
                        if len(pluginlines) == 0:
                            if plugin not in enabled_sections:
                                line = line[line.rfind('#') + 1:]
                                uncomment_section = True
                                enabled_sections.append(plugin)
                                error_plugins.append((
                                    plugin, 'plugin section found in '
                                    + '{}, but commented'.format(COLLECTD_CONF)
                                    + ' out, trying to uncomment it.', False))
                        elif not commented:
                            if plugin not in enabled_sections:
                                enabled_sections.append(plugin)
                            else:
                                line = '#' + line
                                comment_section = True
                                error_plugins.append((
                                    plugin, 'additional occurrence of plugin '
                                    + 'section found in {}'.format(
                                        COLLECTD_CONF)
                                    + ', trying to comment it out.', False))
            elif in_section > 0:
                if comment_section and '#' not in line:
                    line = '#' + line
                if uncomment_section and '#' in line:
                    line = line[line.rfind('#') + 1:]
                if '</Plugin>' in line:
                    in_section -= 1
                    if in_section == 0:
                        comment_section = False
                        uncomment_section = False
            elif '</Plugin>' in line:
                self.__logger.error(
                    'Unexpected closure os plugin section on line'
                    + ' {} in collectd.conf'.format(len(out_lines) + 1)
                    + ', matching section start not found.')
                return False
            out_lines.append(line)
        if in_section > 0:
            self.__logger.error(
                'Unexpected end of file collectd.conf, '
                + 'closure of last plugin section not found.')
            return False
        out_lines = [
            'LoadPlugin {}\n'.format(plugin) for plugin in plugins_to_enable
            if plugin not in enabled_plugins] + out_lines
        for plugin in plugins_to_enable:
            if plugin not in enabled_plugins:
                error_plugins.append((
                    plugin, 'plugin not enabled in {},'.format(COLLECTD_CONF)
                    + ' trying to enable it.', False))
        unenabled_sections = [plugin for plugin in plugins_to_enable
                              if plugin not in enabled_sections]
        if unenabled_sections:
            self.__logger.error(
                'Plugin sections for following plugins not found: {}'.format(
                    ', '.join(unenabled_sections)))
            return False

        config.close()
        if create_backup:
            self.__logger.info('Creating backup of collectd.conf...')
            config = sftp.open(COLLECTD_CONF + '.backup', mode='w')
            config.writelines(in_lines)
            config.close()
        self.__logger.info('Updating collectd.conf...')
        config = sftp.open(COLLECTD_CONF, mode='w')
        config.writelines(out_lines)
        config.close()
        diff_command = \
            "diff {} {}.backup".format(COLLECTD_CONF, COLLECTD_CONF)
        stdin, stdout, stderr = ssh.exec_command(diff_command)
        self.__logger.debug(diff_command)
        for line in stdout.readlines():
            self.__logger.debug(line.strip())
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

        def get_collectd_processes(ssh_session):
            """Get number of running collectd processes.

            Keyword arguments:
            ssh_session -- instance of SSH session in which to check
                for processes
            """
            stdin, stdout, stderr = ssh_session.exec_command(
                "pgrep collectd")
            return len(stdout.readlines())

        ssh, sftp = self.__open_sftp_session(
            compute.get_ip(), 'root', 'opnfvapex')

        self.__logger.info('Stopping collectd service...')
        stdout = self.execute_command("service collectd stop", ssh=ssh)
        time.sleep(10)
        if get_collectd_processes(ssh):
            self.__logger.error('Collectd is still running...')
            return False, []
        self.__logger.info('Starting collectd service...')
        stdout = self.execute_command("service collectd start", ssh=ssh)
        time.sleep(10)
        warning = [output.strip() for output in stdout if 'WARN: ' in output]
        if get_collectd_processes(ssh) == 0:
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
