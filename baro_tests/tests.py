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

"""Function for testing collectd plug-ins with different oup plug-ins"""

import time
import math


def test_snmp_sends_data(
        compute, interval, logger, client, mib_file=None,
        mib_strings=None, in_command=None, conf=None):
    """Check that SNMP deta are updated"""
    logger.debug('Interval: {}'.format(interval))
    if mib_file is not None:
        logger.info(
            'Getting SNMP metrics of MIB file {} and '.format(mib_file)
            + 'following MIB strings: {}...'.format(', '.join(mib_strings)))
    snmp_metrics = client.get_snmp_metrics(compute, mib_file, mib_strings)
    if mib_file is None:
        return len(snmp_metrics) > 1
    if in_command is not None and conf is not None:
        conf.execute_command(in_command, compute.get_ip())

    attempt = 1
    is_passed = False
    while (attempt <= 10) and not is_passed:
        is_passed = True
        # wait Interval time + 2 sec for db update
        sleep_time = interval + 2
        if attempt > 1:
            logger.info('Starting attempt {}'.format(attempt))
        logger.info(
            'Sleeping for {} seconds to get updated entries'.format(sleep_time)
            + ' (interval is {} sec)...'.format(interval))
        time.sleep(sleep_time)

        logger.info(
            'Getting SNMP metrics of MIB file {} and '.format(mib_file)
            + 'following MIB strings: {}...'.format(', '.join(mib_strings)))
        snmp_metrics2 = client.get_snmp_metrics(compute, mib_file, mib_strings)
        unchanged_snmp_metrics = [
            snmp_metric for snmp_metric in snmp_metrics
            if snmp_metrics[snmp_metric] == snmp_metrics2[snmp_metric]]
        if len(unchanged_snmp_metrics) > 0:
            logger.error("Following SNMP metrics didn't change: {}".format(
                ', '.join(unchanged_snmp_metrics)))
            is_passed = False
        attempt += 1
        if not is_passed:
            logger.warning('After sleep new entries were not found.')
    if not is_passed:
        logger.error('This was the last attempt.')
        return False
    logger.info('All SNMP metrics are changed.')
    return True


def test_ceilometer_node_sends_data(
        node_id, interval, logger, client, criteria_list=[],
        resource_id_substrings=['']):
    """ Test that data reported by Ceilometer are updated in the given interval.

    Keyword arguments:
    node_id -- node ID
    interval -- interval to check
    logger -- logger instance
    client -- CeilometerClient instance
    criteria_list -- list of criteria used in ceilometer calls
    resource_id_substrings -- list of substrings to search for in resource ID

    Return boolean value indicating success or failure.
    """

    def _search_meterlist_latest_entry(meterlist, node_str, substr=''):
        """Search for latest entry in meter list

        Keyword arguments:
        meterlist -- list of metrics
        node_str -- name of node, which will be found in meter list
        substr -- substring which will be found in meter list

        Return latest entry from meter list which contains given node string
        and (if defined) subsrting.
        """
        res = [
            entry for entry in meterlist if node_str in entry['resource_id']
            and substr in entry['resource_id']]
        if res:
            return res[0]
        else:
            return []

    client.auth_token()
    timestamps = {}
    node_str = 'node-{}'.format(node_id) if node_id else ''

    logger.info(
        'Searching for timestamps of latest entries{0}{1}{2}...'.format(
            '' if node_str == '' else ' for {}'.format(node_str),
            '' if len(criteria_list) == 0 else (
                ' for criteria ' + ', '.join(criteria_list)),
            '' if resource_id_substrings == [''] else
            ' and resource ID substrings "{}"'.format(
                '", "'.join(resource_id_substrings))))
    for criterion in criteria_list if len(criteria_list) > 0 else [None]:
        meter_list = client.get_gnocchi_metrics(criterion)
        for resource_id_substring in resource_id_substrings:
            last_entry = _search_meterlist_latest_entry(
                meter_list, node_str, resource_id_substring)
            if len(last_entry) == 0:
                logger.error('Entry{0}{1}{2} not found'.format(
                    '' if node_str == '' else ' for {}'.format(node_str),
                    '' if criterion is None else 'for criterion {}'.format(
                        criterion),
                    '' if resource_id_substring == '' else 'and resource '
                    + 'ID substring "{}"'.format(resource_id_substring)))
                return False
            timestamp = last_entry['timestamp']
            logger.debug('Last entry found: {0} {1}'.format(
                timestamp, last_entry['resource_id']))
            timestamps[(criterion, resource_id_substring)] = timestamp

    attempt = 1
    is_passed = False
    while (attempt <= 10) and not is_passed:
        is_passed = True
        # wait Interval time + 2 sec for db update
        sleep_time = interval + 2
        if attempt > 1:
            logger.info('Starting attempt {}'.format(attempt))
        logger.info(
            'Sleeping for {} seconds to get updated entries '.format(sleep_time)
            + '(interval is {} sec)...'.format(interval))
        time.sleep(sleep_time)

        logger.info(
            'Searching for timestamps of latest entries{}{}{}...' .format(
                '' if node_str == '' else ' for {}'.format(node_str),
                '' if len(criteria_list) == 0 else (
                    ' for criteria ' + ', ' .join(criteria_list)),
                '' if resource_id_substrings == ['']
                else ' and resource ID substrings "{}"' .format(
                    '", "'.join(resource_id_substrings))))
        for criterion in criteria_list if len(criteria_list) > 0 else [None]:
            meter_list = client.get_ceil_metrics(criterion)
            for resource_id_substring in resource_id_substrings:
                last_entry = _search_meterlist_latest_entry(
                    meter_list, node_str, resource_id_substring)
                if len(last_entry) == 0:
                    logger.error('Entry{0}{1}{2} not found'.format(
                        '' if node_str == '' else ' for {}'.format(node_str),
                        '' if criterion is None else 'for criterion {}'.format(
                            criterion),
                        '' if resource_id_substring == '' else ' and resource'
                        + 'ID substring "{}"'.format(resource_id_substring)))
                    return False
                timestamp = last_entry['timestamp']
                logger.debug('Last entry found: {} {}'.format(
                    timestamp, last_entry['resource_id']))
                if timestamp == timestamps[(criterion, resource_id_substring)]:
                    logger.warning(
                        'Last entry{0}{1}{2} has the same timestamp as '
                        + 'before the sleep'.format(
                            '' if node_str == '' else ' for {}'.format(
                                node_str),
                            '' if resource_id_substring == ''
                            else ', substring "{}"'.format(
                                resource_id_substring),
                            '' if criterion is None else
                            ' for criterion {}'.format(criterion)))
                    is_passed = False
        attempt += 1
        if not is_passed:
            logger.warning('After sleep new entries were not found.')
    if not is_passed:
        logger.error('This was the last attempt.')
        return False
    logger.info('All latest entries found.')
    return True


def test_csv_handles_plugin_data(
        compute, interval, plugin, plugin_subdirs, meter_categories,
        logger, client):
    """Check that CSV data are updated by the plugin.

    Keyword arguments:
    compute -- object compute node
    interval -- interval to check
    plugin -- plugin which will be tested
    plugin_subdirs -- list subdirectories in csv folder
    meter_categories -- list of meter categories which will be tested
    logger -- logger instance
    client -- CSVClient instance

    Return boolean value indicating success or failure.
    """
    logger.info(
        'Getting CSV metrics of plugin {} on compute node {}...' .format(
            plugin, compute.get_id()))
    logger.debug('Interval: {}'.format(interval))
    logger.debug('Plugin subdirs: {}'.format(plugin_subdirs))
    logger.debug('Plugin meter categories: {}'.format(meter_categories))
    plugin_metrics = client.get_csv_metrics(
        compute, plugin_subdirs, meter_categories)
    if len(plugin_metrics) < len(plugin_subdirs) * len(meter_categories):
        logger.error('Some plugin metrics not found')
        return False

    logger.info(
        'Checking that last two entries in metrics are corresponding'
        + 'to interval...')
    for metric in plugin_metrics:
        logger.debug('{0} {1} {2} ... '.format(metric[0], metric[1], metric[2]))
        # When there's a small interval or many metrics, there may be a slight
        # delay in writing the metrics. e.g. a gap of 1.* is okay for an interval of 1
        if math.floor(metric[3] - metric[2]) > interval + 1:
            logger.error(
                'Time of last two entries differ by '
                + '{}, but interval is {}'.format(
                    metric[3] - metric[2], interval))
            return False
        else:
            logger.debug('OK')
    logger.info('OK')

    # wait Interval time + 2 sec
    sleep_time = interval + 2
    logger.info(
        'Sleeping for {} seconds to get updated entries '.format(sleep_time)
        + '(interval is {} sec)...'.format(interval))
    time.sleep(sleep_time)

    logger.info('Getting new metrics of compute node {}...'.format(
        compute.get_name()))
    plugin_metrics2 = client.get_csv_metrics(
        compute, plugin_subdirs, meter_categories)
    if len(plugin_metrics2) < len(plugin_subdirs) * len(meter_categories):
        logger.error('Some plugin metrics not found')
        return False

    logger.info('Comparing old and new metrics...')
    logger.debug(plugin_metrics)
    logger.debug(plugin_metrics2)
    if len(plugin_metrics) != len(plugin_metrics2):
        logger.error('Plugin metrics length before and after sleep differ')
        return False
    for i in range(len(plugin_metrics2)):
        logger.debug('{0} {1} {2}  - {3} {4} {5} ... '.format(
            plugin_metrics[i][0], plugin_metrics[i][1],
            plugin_metrics[i][2], plugin_metrics2[i][0],
            plugin_metrics2[i][1], plugin_metrics2[i][2]))
        if plugin_metrics[i] == plugin_metrics2[i]:
            logger.error('FAIL')
            return False
        else:
            logger.debug('OK')
    logger.info('OK')

    return True


def test_dma_server_set_collectd(compute, file, logger, client):
    with open(file, mode='w') as f:
        f.write('# dummy conf\n')
    res = client.set(file)
    if res:
        logger.info('set collectd PASS')
    else:
        logger.error('set collectd FAIL')

    return res
