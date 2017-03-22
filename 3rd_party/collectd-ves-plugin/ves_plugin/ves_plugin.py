# MIT License
#
# Copyright(c) 2016-2017 Intel Corporation. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import collectd
import json
import sys
import base64
import urllib2
import socket
import time
from threading import Timer
from threading import Lock

class Event(object):
    """Event header"""

    def __init__(self):
        """Construct the common header"""
        self.version = 1.1
        self.event_type = "Info" # use "Info" unless a notification is generated
        self.domain = ""
        self.event_id = ""
        self.source_id = ""
        self.source_name = ""
        self.functional_role = ""
        self.reporting_entity_id = ""
        self.reporting_entity_name = ""
        self.priority = "Normal" # will be derived from event if there is one
        self.start_epoch_microsec = 0
        self.last_epoch_micro_sec = 0
        self.sequence = 0

    def get_json(self):
        """Get the object of the datatype"""
        obj = {}
        obj['version'] = self.version
        obj['eventType'] = self.event_type
        obj['domain'] = self.domain
        obj['eventId'] = self.event_id
        obj['sourceId'] = self.source_id
        obj['sourceName'] = self.source_name
        obj['functionalRole'] = self.functional_role
        obj['reportingEntityId'] = self.reporting_entity_id
        obj['reportingEntityName'] = self.reporting_entity_name
        obj['priority'] = self.priority
        obj['startEpochMicrosec'] = self.start_epoch_microsec
        obj['lastEpochMicrosec'] = self.last_epoch_micro_sec
        obj['sequence'] = self.sequence
        return json.dumps({
            'event' : {
                'commonEventHeader' : obj,
                self.get_name() : self.get_obj()
            }
        })

    def get_name():
        assert False, 'abstract method get_name() is not implemented'

    def get_obj():
        assert False, 'abstract method get_obj() is not implemented'

class MeasurementGroup(object):
    """MeasurementGroup datatype"""

    def __init__(self, name):
        self.name = name
        self.measurement = []
        pass

    def add_measurement(self, name, value):
        self.measurement.append({
            'name' : name,
            'value' : value
        })

    def get_obj(self):
        return {
            'name' : self.name,
            'measurements' : self.measurement
        }

class MeasurementsForVfScaling(Event):
    """MeasurementsForVfScaling datatype"""

    def __init__(self, event_id):
        """Construct the header"""
        super(MeasurementsForVfScaling, self).__init__()
        # common attributes
        self.domain = "measurementsForVfScaling"
        self.event_id = event_id
        # measurement attributes
        self.additional_measurements = []
        self.aggregate_cpu_usage = 0
        self.codec_usage_array = []
        self.concurrent_sessions = 0
        self.configured_entities = 0
        self.cpu_usage_array = []
        self.errors = []
        self.feature_usage_array = []
        self.filesystem_usage_array = []
        self.latency_distribution = []
        self.mean_request_latency = 0
        self.measurement_fields_version = 1.1
        self.measurement_interval = 0
        self.memory_configured = 0
        self.memory_used = 0
        self.number_of_media_ports_in_use = 0
        self.request_rate = 0
        self.vnfc_scaling_metric = 0
        self.v_nic_usage_array = []

    def add_measurement_group(self, group):
        self.additional_measurements.append(group.get_obj())

    def add_cpu_usage(self, cpu_identifier, usage):
        self.cpu_usage_array.append({
            'cpuIdentifier' : cpu_identifier,
            'percentUsage' : usage
        })

    def add_v_nic_usage(self, if_name, if_pkts, if_bytes):
        self.v_nic_usage_array.append({
            'broadcastPacketsIn' : 0.0,
            'broadcastPacketsOut' : 0.0,
            'multicastPacketsIn' : 0.0,
            'multicastPacketsOut' : 0.0,
            'unicastPacketsIn' : 0.0,
            'unicastPacketsOut' : 0.0,
            'vNicIdentifier' : if_name,
            'packetsIn' : if_pkts[0],
            'packetsOut' : if_pkts[1],
            'bytesIn' : if_bytes[0],
            'bytesOut' : if_bytes[1]
        })

    def get_obj(self):
        """Get the object of the datatype"""
        obj = {}
        obj['additionalMeasurements'] = self.additional_measurements
        obj['aggregateCpuUsage'] = self.aggregate_cpu_usage
        obj['codecUsageArray'] = self.codec_usage_array
        obj['concurrentSessions'] = self.concurrent_sessions
        obj['configuredEntities'] = self.configured_entities
        obj['cpuUsageArray'] = self.cpu_usage_array
        obj['errors'] = self.errors
        obj['featureUsageArray'] = self.feature_usage_array
        obj['filesystemUsageArray'] = self.filesystem_usage_array
        obj['latencyDistribution'] = self.latency_distribution
        obj['meanRequestLatency'] = self.mean_request_latency
        obj['measurementFieldsVersion'] = self.measurement_fields_version
        obj['measurementInterval'] = self.measurement_interval
        obj['memoryConfigured'] = self.memory_configured
        obj['memoryUsed'] = self.memory_used
        obj['numberOfMediaPortsInUse'] = self.number_of_media_ports_in_use
        obj['requestRate'] = self.request_rate
        obj['vnfcScalingMetric'] = self.vnfc_scaling_metric
        obj['vNicUsageArray'] = self.v_nic_usage_array
        return obj

    def get_name(self):
        """Name of datatype"""
        return "measurementsForVfScalingFields"

class Fault(Event):
    """Fault datatype"""

    def __init__(self, event_id):
        """Construct the header"""
        super(Fault, self).__init__()
        # common attributes
        self.domain = "fault"
        self.event_id = event_id
        self.event_type = "Fault"
        # fault attributes
        self.fault_fields_version = 1.1
        self.event_severity = 'NORMAL'
        self.event_source_type = 'other(0)'
        self.alarm_condition = ''
        self.specific_problem = ''
        self.vf_status = 'Active'
        self.alarm_interface_a = ''
        self.alarm_additional_information = []

    def get_name(self):
        """Name of datatype"""
        return 'faultFields'

    def get_obj(self):
        """Get the object of the datatype"""
        obj = {}
        obj['faultFieldsVersion'] = self.fault_fields_version
        obj['eventSeverity'] = self.event_severity
        obj['eventSourceType'] = self.event_source_type
        obj['alarmCondition'] = self.alarm_condition
        obj['specificProblem'] = self.specific_problem
        obj['vfStatus'] = self.vf_status
        obj['alarmInterfaceA'] = self.alarm_interface_a
        obj['alarmAdditionalInformation'] = self.alarm_additional_information
        return obj

class VESPlugin(object):
    """VES plugin with collectd callbacks"""

    def __init__(self):
        """Plugin initialization"""
        self.__plugin_data_cache = {
            'cpu' : {'interval' : 0.0, 'vls' : []},
            'cpu-aggregation' : {'interval' : 0.0, 'vls' : []},
            'virt' : {'interval' : 0.0, 'vls' : []},
            'disk' : {'interval' : 0.0, 'vls' : []},
            'interface' : {'interval' : 0.0, 'vls' : []},
            'memory' : {'interval' : 0.0, 'vls' : []}
        }
        self.__plugin_config = {
            'Domain' : '127.0.0.1',
            'Port' : 30000.0,
            'Path' : '',
            'Username' : '',
            'Password' : '',
            'Topic' : '',
            'UseHttps' : False,
            'SendEventInterval' : 20.0,
            'FunctionalRole' : 'Collectd VES Agent',
            'GuestRunning' : False
        }
        self.__host_name = None
        self.__ves_timer = None
        self.__event_timer_interval = 20.0
        self.__lock = Lock()
        self.__event_id = 0

    def get_event_id(self):
        """get event id"""
        self.__event_id += 1
        return str(self.__event_id)

    def lock(self):
        """Lock the plugin"""
        self.__lock.acquire()

    def unlock(self):
        """Unlock the plugin"""
        self.__lock.release()

    def start_timer(self):
        """Start event timer"""
        self.__ves_timer = Timer(self.__event_timer_interval, self.__on_time)
        self.__ves_timer.start()

    def stop_timer(self):
        """Stop event timer"""
        self.__ves_timer.cancel()

    def __on_time(self):
        """Timer thread"""
        self.start_timer()
        self.event_timer()

    def event_send(self, event):
        """Send event to VES"""
        server_url = "http{}://{}:{}/{}eventListener/v3{}".format(
            's' if self.__plugin_config['UseHttps'] else '', self.__plugin_config['Domain'],
            int(self.__plugin_config['Port']), '{}/'.format(
            '/{}'.format(self.__plugin_config['Path'])) if (len(self.__plugin_config['Path']) > 0) else '',
            self.__plugin_config['Topic'])
        collectd.info('Vendor Event Listener is at: {}'.format(server_url))
        credentials = base64.b64encode('{}:{}'.format(
            self.__plugin_config['Username'], self.__plugin_config['Password']))
        collectd.info('Authentication credentials are: {}'.format(credentials))
        try:
            request = urllib2.Request(server_url)
            request.add_header('Authorization', 'Basic {}'.format(credentials))
            request.add_header('Content-Type', 'application/json')
            collectd.debug("Sending {} to {}".format(event.get_json(), server_url))
            vel = urllib2.urlopen(request, event.get_json(), timeout=1)
        except urllib2.HTTPError as e:
            collectd.error('Vendor Event Listener exception: {}'.format(e))
        except urllib2.URLError as e:
            collectd.error('Vendor Event Listener is is not reachable: {}'.format(e))

    def bytes_to_gb(self, bytes):
        """Convert bytes to GB"""
        return round((bytes / 1073741824.0), 3)

    def get_hostname(self):
        if len(self.__host_name):
            return self.__host_name
        return socket.gethostname()

    def event_timer(self):
        """Event timer thread"""
        self.lock()
        try:
            if (self.__plugin_config['GuestRunning']):
                # if we running on a guest only, send 'additionalMeasurements' only
                measurement = MeasurementsForVfScaling(self.get_event_id())
                measurement.functional_role = self.__plugin_config['FunctionalRole']
                # add host/guest values as additional measurements
                self.fill_additional_measurements(measurement, exclude_plugins=[
                    'cpu', 'cpu-aggregation', 'memory', 'disk', 'interface', 'virt'])
                # fill out reporting & source entities
                reporting_entity = self.get_hostname()
                measurement.reporting_entity_id = reporting_entity
                measurement.reporting_entity_name = reporting_entity
                measurement.source_id = reporting_entity
                measurement.source_name = measurement.source_id
                measurement.start_epoch_microsec = (time.time() * 1000000)
                measurement.measurement_interval = self.__plugin_config['SendEventInterval']
                # total CPU
                total_cpu_system = self.cache_get_value(plugin_name='cpu-aggregation', type_instance='system')
                total_cpu_user = self.cache_get_value(plugin_name='cpu-aggregation', type_instance='user')
                measurement.aggregate_cpu_usage = round(total_cpu_system[0]['values'][0] +
                                                    total_cpu_user[0]['values'][0], 2)
                # CPU per each instance
                cpux_system = self.cache_get_value(plugin_name='cpu', type_instance='system',
                                                  mark_as_read = False)
                for cpu_inst in [x['plugin_instance'] for x in cpux_system]:
                    cpu_system = self.cache_get_value(plugin_name='cpu',
                                                      plugin_instance=cpu_inst, type_instance='system')
                    cpu_user = self.cache_get_value(plugin_name='cpu',
                                                      plugin_instance=cpu_inst, type_instance='user')
                    cpu_usage = round(cpu_system[0]['values'][0] + cpu_user[0]['values'][0], 2)
                    measurement.add_cpu_usage(cpu_inst, cpu_usage)
                # fill memory used
                memory_used = self.cache_get_value(plugin_name='memory', type_name='memory', type_instance='used')
                if len(memory_used) > 0:
                    measurement.memory_used = self.bytes_to_gb(memory_used[0]['values'][0])
                # if_packets
                ifinfo = {}
                if_stats = self.cache_get_value(plugin_name='interface', type_name='if_packets')
                if len(if_stats) > 0:
                    for if_stat in if_stats:
                        ifinfo[if_stat['plugin_instance']] = {
                            'pkts' : (if_stat['values'][0], if_stat['values'][1])
                        }
                # go through all interfaces and get if_octets
                for if_name in ifinfo.keys():
                    if_stats = self.cache_get_value(plugin_instance=if_name, plugin_name='interface',
                                                    type_name='if_octets')
                    if len(if_stats) > 0:
                        ifinfo[if_name]['bytes'] = (if_stats[0]['values'][0], if_stats[0]['values'][1])
                # fill vNicUsageArray filed in the event
                for if_name in ifinfo.keys():
                    measurement.add_v_nic_usage(if_name, ifinfo[if_name]['pkts'], ifinfo[if_name]['bytes'])
                # send event to the VES
                self.event_send(measurement)
                return
            # get list of all VMs
            virt_vcpu_total = self.cache_get_value(plugin_name='virt', type_name='virt_cpu_total',
                                                   mark_as_read=False)
            vm_names = [x['plugin_instance'] for x in virt_vcpu_total]
            for vm_name in vm_names:
                # make sure that 'virt' plugin cache is up-to-date
                vm_values = self.cache_get_value(plugin_name='virt', plugin_instance=vm_name,
                                                 mark_as_read=False)
                us_up_to_date = True
                for vm_value in vm_values:
                    if vm_value['updated'] == False:
                        us_up_to_date = False
                        break
                if not us_up_to_date:
                        # one of the cache value is not up-to-date, break
                        collectd.warning("virt collectD cache values are not up-to-date for {}".format(vm_name))
                        continue
                # if values are up-to-date, create an event message
                measurement = MeasurementsForVfScaling(self.get_event_id())
                measurement.functional_role = self.__plugin_config['FunctionalRole']
                # fill out reporting_entity
                reporting_entity = '{}-{}-{}'.format(self.get_hostname(), 'virt', vm_name)
                measurement.reporting_entity_id = reporting_entity
                measurement.reporting_entity_name = reporting_entity
                # virt_cpu_total
                virt_vcpu_total = self.cache_get_value(plugin_instance=vm_name,
                                                       plugin_name='virt', type_name='virt_cpu_total')
                if len(virt_vcpu_total) > 0:
                    measurement.aggregate_cpu_usage = self.cpu_ns_to_percentage(virt_vcpu_total[0])
                    # set source as a host for virt_vcpu_total value
                    measurement.source_id = virt_vcpu_total[0]['host']
                    measurement.source_name = measurement.source_id
                    # fill out EpochMicrosec (convert to us)
                    measurement.start_epoch_microsec = (virt_vcpu_total[0]['time'] * 1000000)
                # virt_vcp
                virt_vcpus = self.cache_get_value(plugin_instance=vm_name,
                                                  plugin_name='virt', type_name='virt_vcpu')
                if len(virt_vcpus) > 0:
                    for virt_vcpu in virt_vcpus:
                        cpu_usage = self.cpu_ns_to_percentage(virt_vcpu)
                        measurement.add_cpu_usage(virt_vcpu['type_instance'], cpu_usage)
                # plugin interval
                measurement.measurement_interval = self.__plugin_data_cache['virt']['interval']
                # memory-total
                memory_total = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                    type_name='memory', type_instance='total')
                if len(memory_total) > 0:
                    measurement.memory_configured = self.bytes_to_gb(memory_total[0]['values'][0])
                # memory-rss
                memory_rss = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                  type_name='memory', type_instance='rss')
                if len(memory_rss) > 0:
                    measurement.memory_used = self.bytes_to_gb(memory_rss[0]['values'][0])
                # if_packets
                ifinfo = {}
                if_stats = self.cache_get_value(plugin_instance=vm_name,
                                                plugin_name='virt', type_name='if_packets')
                if len(if_stats) > 0:
                    for if_stat in if_stats:
                        ifinfo[if_stat['type_instance']] = {
                            'pkts' : (if_stat['values'][0], if_stat['values'][1])
                        }
                # go through all interfaces and get if_octets
                for if_name in ifinfo.keys():
                    if_stats = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                    type_name='if_octets', type_instance=if_name)
                    if len(if_stats) > 0:
                        ifinfo[if_name]['bytes'] = (if_stats[0]['values'][0], if_stats[0]['values'][1])
                # fill vNicUsageArray filed in the event
                for if_name in ifinfo.keys():
                    measurement.add_v_nic_usage(if_name, ifinfo[if_name]['pkts'], ifinfo[if_name]['bytes'])
                # add host/guest values as additional measurements
                self.fill_additional_measurements(measurement, ['virt'])
                # send event to the VES
                self.event_send(measurement)
        finally:
            self.unlock()

    def fill_additional_measurements(self, measurement, exclude_plugins=None):
        """Fill out addition measurement filed with host/guets values"""
        # add host/guest values as additional measurements
        for plugin_name in self.__plugin_data_cache.keys():
            if (exclude_plugins != None and plugin_name in exclude_plugins):
                # skip host-only values
                continue;
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                if val['updated']:
                    mgroup_name = '{}{}{}'.format(plugin_name,
                        '-{}'.format(val['plugin_instance']) if len(val['plugin_instance']) else '',
                        '-{}'.format(val['type_instance']) if len(val['type_instance']) else '')
                    mgroup = MeasurementGroup(mgroup_name)
                    ds = collectd.get_dataset(val['type'])
                    for index in xrange(len(ds)):
                        mname = '{}-{}'.format(val['type'], ds[index][0])
                        mgroup.add_measurement(mname, str(val['values'][index]))
                    measurement.add_measurement_group(mgroup);
                    val['updated'] = False

    def cpu_ns_to_percentage(self, vl):
        """Convert CPU usage ns to CPU %"""
        total = vl['values'][0]
        total_time = vl['time']
        pre_total = vl['pre_values'][0]
        pre_total_time = vl['pre_time']
        if (total_time - pre_total_time) == 0:
            # return zero usage if time diff is zero
            return 0.0
        percent = (100.0 * (total - pre_total))/((total_time - pre_total_time) * 1000000000.0)
        collectd.debug("pre_time={}, pre_value={}, time={}, value={}, cpu={}%".format(
            pre_total_time, pre_total, total_time, total, round(percent, 2)))
        return round(percent, 2)

    def config(self, config):
        """Collectd config callback"""
        for child in config.children:
            # check the config entry name
            if child.key not in self.__plugin_config:
                collectd.error("Key '{}' name is invalid".format(child.key))
                raise RuntimeError('Configuration key name error')
            # check the config entry value type
            if len(child.values) == 0 or type(child.values[0]) != type(self.__plugin_config[child.key]):
                collectd.error("Key '{}' value type should be {}".format(
                               child.key, str(type(self.__plugin_config[child.key]))))
                raise RuntimeError('Configuration key value error')
            # store the value in configuration
            self.__plugin_config[child.key] = child.values[0]

    def init(self):
        """Collectd init callback"""
        # start the VES timer
        self.start_timer()

    ##
    # Please note, the cache should be locked before using this function
    #
    def update_cache_value(self, vl):
        """Update value internal collectD cache values or create new one"""
        found = False
        if vl.plugin not in self.__plugin_data_cache:
             self.__plugin_data_cache[vl.plugin] = {'vls': []}
        plugin_vl = self.__plugin_data_cache[vl.plugin]['vls']
        for index in xrange(len(plugin_vl)):
            # record found, so just update time the values
            if (plugin_vl[index]['plugin_instance'] ==
                vl.plugin_instance) and (plugin_vl[index]['type_instance'] ==
                    vl.type_instance) and (plugin_vl[index]['type'] == vl.type):
                plugin_vl[index]['pre_time'] = plugin_vl[index]['time']
                plugin_vl[index]['time'] = vl.time
                plugin_vl[index]['pre_values'] = plugin_vl[index]['values']
                plugin_vl[index]['values'] = vl.values
                plugin_vl[index]['updated'] = True
                found = True
                break
        if not found:
            value = {}
            # create new cache record
            value['plugin_instance'] = vl.plugin_instance
            value['type_instance'] = vl.type_instance
            value['values'] = vl.values
            value['pre_values'] = vl.values
            value['type'] = vl.type
            value['time'] = vl.time
            value['pre_time'] = vl.time
            value['host'] = vl.host
            value['updated'] = True
            self.__plugin_data_cache[vl.plugin]['vls'].append(value)
            # update plugin interval based on one received in the value
            self.__plugin_data_cache[vl.plugin]['interval'] = vl.interval

    def cache_get_value(self, plugin_name=None, plugin_instance=None,
                        type_name=None, type_instance=None, type_names=None, mark_as_read=True):
        """Get cache value by given criteria"""
        ret_list = []
        if plugin_name in self.__plugin_data_cache:
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                #collectd.info("plugin={}, type={}, type_instance={}".format(
                #    plugin_name, val['type'], val['type_instance']))
                if (type_name == None or type_name == val['type']) and (plugin_instance == None
                    or plugin_instance == val['plugin_instance']) and (type_instance == None
                    or type_instance == val['type_instance']) and (type_names == None
                    or val['type'] in type_names):
                    if mark_as_read:
                        val['updated'] = False
                    ret_list.append(val)
        return ret_list

    def write(self, vl, data=None):
        """Collectd write callback"""
        self.lock()
        try:
            # Example of collectD Value format
            # collectd.Values(type='cpu',type_instance='interrupt',
            # plugin='cpu',plugin_instance='25',host='localhost',
            # time=1476694097.022873,interval=10.0,values=[0])
            if vl.plugin == 'ves_plugin':
                # store the host name and unregister callback
                self.__host_name = vl.host
                collectd.unregister_read(self.read)
                return
            # update the cache values
            self.update_cache_value(vl)
        finally:
            self.unlock()

    def read(self, data=None):
        """Collectd read callback. Use this callback to get host name"""
        vl = collectd.Values(type='gauge')
        vl.plugin='ves_plugin'
        vl.dispatch(values=[0])

    def notify(self, n):
        """Collectd notification callback"""
        collectd_event_severity_map = {
            collectd.NOTIF_FAILURE : 'CRITICAL',
            collectd.NOTIF_WARNING : 'WARNING',
            collectd.NOTIF_OKAY : 'NORMAL'
        }
        fault = Fault(self.get_event_id())
        # fill out common header
        fault.event_type = "Notification"
        fault.functional_role = self.__plugin_config['FunctionalRole']
        fault.reporting_entity_id = self.get_hostname()
        fault.reporting_entity_name = self.get_hostname()
        fault.source_id = self.get_hostname()
        fault.source_name = self.get_hostname()
        fault.start_epoch_microsec = (n.time * 1000000)
        fault.last_epoch_micro_sec = fault.start_epoch_microsec
        # fill out fault header
        fault.event_severity = collectd_event_severity_map[n.severity]
        fault.specific_problem = '{}{}'.format('{}-'.format(n.plugin_instance
            if len(n.plugin_instance) else ''), n.type_instance)
        fault.alarm_interface_a = '{}{}'.format(n.plugin, '-{}'.format(
            n.plugin_instance if len(n.plugin_instance) else ''))
        fault.event_source_type = 'virtualMachine(8)' if self.__plugin_config['GuestRunning'] else 'host(3)'
        fault.alarm_condition = n.message
        self.event_send(fault)

    def shutdown(self):
        """Collectd shutdown callback"""
        # stop the timer
        self.stop_timer()

# The collectd plugin instance
plugin_instance = VESPlugin()

# Register plugin callbacks
collectd.register_config(plugin_instance.config)
collectd.register_init(plugin_instance.init)
collectd.register_read(plugin_instance.read)
collectd.register_write(plugin_instance.write)
collectd.register_notification(plugin_instance.notify)
collectd.register_shutdown(plugin_instance.shutdown)
