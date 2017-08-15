#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import base64
import ConfigParser
import logging
import argparse

from distutils.util import strtobool
from kafka import KafkaConsumer

try:
    # For Python 3.0 and later
    import urllib.request as url
except ImportError:
    # Fall back to Python 2's urllib2
    import urllib2 as url
import socket
import time
from threading import Timer
from threading import Lock


class Event(object):
    """Event header"""

    def __init__(self):
        """Construct the common header"""
        self.version = 2.0
        self.event_type = "Info"  # use "Info" unless a notification is generated
        self.domain = ""
        self.event_id = ""
        self.source_id = ""
        self.source_name = ""
        self.functional_role = ""
        self.reporting_entity_id = ""
        self.reporting_entity_name = ""
        self.priority = "Normal"  # will be derived from event if there is one
        self.start_epoch_microsec = 0
        self.last_epoch_micro_sec = 0
        self.sequence = 0
        self.event_name = ""
        self.internal_header_fields = {}
        self.nfc_naming_code = ""
        self.nf_naming_code = ""

    def get_json(self):
        """Get the object of the datatype"""
        obj = {}
        obj['version'] = self.version
        obj['eventType'] = self.event_type
        obj['domain'] = self.domain
        obj['eventId'] = self.event_id
        obj['sourceId'] = self.source_id
        obj['sourceName'] = self.source_name
        obj['reportingEntityId'] = self.reporting_entity_id
        obj['reportingEntityName'] = self.reporting_entity_name
        obj['priority'] = self.priority
        obj['startEpochMicrosec'] = self.start_epoch_microsec
        obj['lastEpochMicrosec'] = self.last_epoch_micro_sec
        obj['sequence'] = self.sequence
        obj['eventName'] = self.event_name
        obj['internalHeaderFields'] = self.internal_header_fields
        obj['nfcNamingCode'] = self.nfc_naming_code
        obj['nfNamingCode'] = self.nf_naming_code
        return json.dumps({
            'event': {
                'commonEventHeader': obj,
                self.get_name(): self.get_obj()
            }
        }).encode()

    def get_name():
        assert False, 'abstract method get_name() is not implemented'

    def get_obj():
        assert False, 'abstract method get_obj() is not implemented'


class Field(object):
    """field datatype"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_obj(self):
        return {
            'name': self.name,
            'value': self.value
        }


class NamedArrayOfFields(object):
    """namedArrayOfFields datatype"""

    def __init__(self, name):
        self.name = name
        self.array_of_fields = []

    def add(self, field):
        self.array_of_fields.append(field.get_obj())

    def get_obj(self):
        return {
            'name': self.name,
            'arrayOfFields': self.array_of_fields
        }


class VESDataType(object):
    """ Base VES datatype """

    def set_optional(self, obj, key, val):
        if val is not None:
            obj[key] = val


class DiskUsage(VESDataType):
    """diskUsage datatype"""

    def __init__(self, identifier):
        self.disk_identifier = identifier
        self.disk_io_time_avg = None
        self.disk_io_time_last = None
        self.disk_io_time_max = None
        self.disk_io_time_min = None
        self.disk_merged_read_avg = None
        self.disk_merged_read_last = None
        self.disk_merged_read_max = None
        self.disk_merged_read_min = None
        self.disk_merged_write_avg = None
        self.disk_merged_write_last = None
        self.disk_merged_write_max = None
        self.disk_merged_write_min = None
        self.disk_octets_read_avg = None
        self.disk_octets_read_last = None
        self.disk_octets_read_max = None
        self.disk_octets_read_min = None
        self.disk_octets_write_avg = None
        self.disk_octets_write_last = None
        self.disk_octets_write_max = None
        self.disk_octets_write_min = None
        self.disk_ops_read_avg = None
        self.disk_ops_read_last = None
        self.disk_ops_read_max = None
        self.disk_ops_read_min = None
        self.disk_ops_write_avg = None
        self.disk_ops_write_last = None
        self.disk_ops_write_max = None
        self.disk_ops_write_min = None
        self.disk_pending_operations_avg = None
        self.disk_pending_operations_last = None
        self.disk_pending_operations_max = None
        self.disk_pending_operations_min = None
        self.disk_time_read_avg = None
        self.disk_time_read_last = None
        self.disk_time_read_max = None
        self.disk_time_read_min = None
        self.disk_time_write_avg = None
        self.disk_time_write_last = None
        self.disk_time_write_max = None
        self.disk_time_write_min = None

    def get_obj(self):
        obj = {
            # required
            'diskIdentifier': self.disk_identifier
        }
        self.set_optional(obj, 'diskIoTimeAvg', self.disk_io_time_avg)
        self.set_optional(obj, 'diskIoTimeLast', self.disk_io_time_last)
        self.set_optional(obj, 'diskIoTimeMax', self.disk_io_time_max)
        self.set_optional(obj, 'diskIoTimeMin', self.disk_io_time_min)
        self.set_optional(obj, 'diskMergedReadAvg', self.disk_merged_read_avg)
        self.set_optional(obj, 'diskMergedReadLast', self.disk_merged_read_last)
        self.set_optional(obj, 'diskMergedReadMax', self.disk_merged_read_max)
        self.set_optional(obj, 'diskMergedReadMin', self.disk_merged_read_min)
        self.set_optional(obj, 'diskMergedWriteAvg', self.disk_merged_write_avg)
        self.set_optional(obj, 'diskMergedWriteLast', self.disk_merged_write_last)
        self.set_optional(obj, 'diskMergedWriteMax', self.disk_merged_write_max)
        self.set_optional(obj, 'diskMergedWriteMin', self.disk_merged_write_min)
        self.set_optional(obj, 'diskOctetsReadAvg', self.disk_octets_read_avg)
        self.set_optional(obj, 'diskOctetsReadLast', self.disk_octets_read_last)
        self.set_optional(obj, 'diskOctetsReadMax', self.disk_octets_read_max)
        self.set_optional(obj, 'diskOctetsReadMin', self.disk_octets_read_min)
        self.set_optional(obj, 'diskOctetsWriteAvg', self.disk_octets_write_avg)
        self.set_optional(obj, 'diskOctetsWriteLast', self.disk_octets_write_last)
        self.set_optional(obj, 'diskOctetsWriteMax', self.disk_octets_write_max)
        self.set_optional(obj, 'diskOctetsWriteMin', self.disk_octets_write_min)
        self.set_optional(obj, 'diskOpsReadAvg', self.disk_ops_read_avg)
        self.set_optional(obj, 'diskOpsReadLast', self.disk_ops_read_last)
        self.set_optional(obj, 'diskOpsReadMax', self.disk_ops_read_max)
        self.set_optional(obj, 'diskOpsReadMin', self.disk_ops_read_min)
        self.set_optional(obj, 'diskOpsWriteAvg', self.disk_ops_write_avg)
        self.set_optional(obj, 'diskOpsWriteLast', self.disk_ops_write_last)
        self.set_optional(obj, 'diskOpsWriteMax', self.disk_ops_write_max)
        self.set_optional(obj, 'diskOpsWriteMin', self.disk_ops_write_min)
        self.set_optional(obj, 'diskPendingOperationsAvg', self.disk_pending_operations_avg)
        self.set_optional(obj, 'diskPendingOperationsLast', self.disk_pending_operations_last)
        self.set_optional(obj, 'diskPendingOperationsMax', self.disk_pending_operations_max)
        self.set_optional(obj, 'diskPendingOperationsMin', self.disk_pending_operations_min)
        self.set_optional(obj, 'diskTimeReadAvg', self.disk_time_read_avg)
        self.set_optional(obj, 'diskTimeReadLast', self.disk_time_read_last)
        self.set_optional(obj, 'diskTimeReadMax', self.disk_time_read_max)
        self.set_optional(obj, 'diskTimeReadMin', self.disk_time_read_min)
        self.set_optional(obj, 'diskTimeWriteAvg', self.disk_time_write_avg)
        self.set_optional(obj, 'diskTimeWriteLast', self.disk_time_write_last)
        self.set_optional(obj, 'diskTimeWriteMax', self.disk_time_write_max)
        self.set_optional(obj, 'diskTimeWriteMin', self.disk_time_write_min)
        return obj


class VNicPerformance(VESDataType):
    """vNicPerformance datatype"""

    def __init__(self, identifier):
        self.received_broadcast_packets_accumulated = None
        self.received_broadcast_packets_delta = None
        self.received_discarded_packets_accumulated = None
        self.received_discarded_packets_delta = None
        self.received_error_packets_accumulated = None
        self.received_error_packets_delta = None
        self.received_multicast_packets_accumulated = None
        self.received_multicast_packets_delta = None
        self.received_octets_accumulated = None
        self.received_octets_delta = None
        self.received_total_packets_accumulated = None
        self.received_total_packets_delta = None
        self.received_unicast_packets_accumulated = None
        self.received_unicast_packets_delta = None
        self.transmitted_broadcast_packets_accumulated = None
        self.transmitted_broadcast_packets_delta = None
        self.transmitted_discarded_packets_accumulated = None
        self.transmitted_discarded_packets_delta = None
        self.transmitted_error_packets_accumulated = None
        self.transmitted_error_packets_delta = None
        self.transmitted_multicast_packets_accumulated = None
        self.transmitted_multicast_packets_delta = None
        self.transmitted_octets_accumulated = None
        self.transmitted_octets_delta = None
        self.transmitted_total_packets_accumulated = None
        self.transmitted_total_packets_delta = None
        self.transmitted_unicast_packets_accumulated = None
        self.transmitted_unicast_packets_delta = None
        self.values_are_suspect = 'true'
        self.v_nic_identifier = identifier

    def get_obj(self):
        obj = {
            # required
            'valuesAreSuspect': self.values_are_suspect,
            'vNicIdentifier': self.v_nic_identifier
        }
        # optional
        self.set_optional(obj, 'receivedBroadcastPacketsAccumulated', self.received_broadcast_packets_accumulated)
        self.set_optional(obj, 'receivedBroadcastPacketsDelta', self.received_broadcast_packets_delta)
        self.set_optional(obj, 'receivedDiscardedPacketsAccumulated', self.received_discarded_packets_accumulated)
        self.set_optional(obj, 'receivedDiscardedPacketsDelta', self.received_discarded_packets_delta)
        self.set_optional(obj, 'receivedErrorPacketsAccumulated', self.received_error_packets_accumulated)
        self.set_optional(obj, 'receivedErrorPacketsDelta', self.received_error_packets_delta)
        self.set_optional(obj, 'receivedMulticastPacketsAccumulated', self.received_multicast_packets_accumulated)
        self.set_optional(obj, 'receivedMulticastPacketsDelta', self.received_multicast_packets_delta)
        self.set_optional(obj, 'receivedOctetsAccumulated', self.received_octets_accumulated)
        self.set_optional(obj, 'receivedOctetsDelta', self.received_octets_delta)
        self.set_optional(obj, 'receivedTotalPacketsAccumulated', self.received_total_packets_accumulated)
        self.set_optional(obj, 'receivedTotalPacketsDelta', self.received_total_packets_delta)
        self.set_optional(obj, 'receivedUnicastPacketsAccumulated', self.received_unicast_packets_accumulated)
        self.set_optional(obj, 'receivedUnicastPacketsDelta', self.received_unicast_packets_delta)
        self.set_optional(obj, 'transmittedBroadcastPacketsAccumulated', self.transmitted_broadcast_packets_accumulated)
        self.set_optional(obj, 'transmittedBroadcastPacketsDelta', self.transmitted_broadcast_packets_delta)
        self.set_optional(obj, 'transmittedDiscardedPacketsAccumulated', self.transmitted_discarded_packets_accumulated)
        self.set_optional(obj, 'transmittedDiscardedPacketsDelta', self.transmitted_discarded_packets_delta)
        self.set_optional(obj, 'transmittedErrorPacketsAccumulated', self.transmitted_error_packets_accumulated)
        self.set_optional(obj, 'transmittedErrorPacketsDelta', self.transmitted_error_packets_delta)
        self.set_optional(obj, 'transmittedMulticastPacketsAccumulated', self.transmitted_multicast_packets_accumulated)
        self.set_optional(obj, 'transmittedMulticastPacketsDelta', self.transmitted_multicast_packets_delta)
        self.set_optional(obj, 'transmittedOctetsAccumulated', self.transmitted_octets_accumulated)
        self.set_optional(obj, 'transmittedOctetsDelta', self.transmitted_octets_delta)
        self.set_optional(obj, 'transmittedTotalPacketsAccumulated', self.transmitted_total_packets_accumulated)
        self.set_optional(obj, 'transmittedTotalPacketsDelta', self.transmitted_total_packets_delta)
        self.set_optional(obj, 'transmittedUnicastPacketsAccumulated', self.transmitted_unicast_packets_accumulated)
        self.set_optional(obj, 'transmittedUnicastPacketsDelta', self.transmitted_unicast_packets_delta)
        return obj


class CpuUsage(VESDataType):
    """cpuUsage datatype"""

    def __init__(self, identifier):
        self.cpu_identifier = identifier
        self.cpu_idle = None
        self.cpu_usage_interrupt = None
        self.cpu_usage_nice = None
        self.cpu_usage_soft_irq = None
        self.cpu_usage_steal = None
        self.cpu_usage_system = None
        self.cpu_usage_user = None
        self.cpu_wait = None
        self.percent_usage = 0

    def get_obj(self):
        obj = {
            # required
            'cpuIdentifier': self.cpu_identifier,
            'percentUsage': self.percent_usage
        }
        # optional
        self.set_optional(obj, 'cpuIdle', self.cpu_idle)
        self.set_optional(obj, 'cpuUsageInterrupt', self.cpu_usage_interrupt)
        self.set_optional(obj, 'cpuUsageNice', self.cpu_usage_nice)
        self.set_optional(obj, 'cpuUsageSoftIrq', self.cpu_usage_soft_irq)
        self.set_optional(obj, 'cpuUsageSteal', self.cpu_usage_steal)
        self.set_optional(obj, 'cpuUsageSystem', self.cpu_usage_system)
        self.set_optional(obj, 'cpuUsageUser', self.cpu_usage_user)
        self.set_optional(obj, 'cpuWait', self.cpu_wait)
        return obj


class MemoryUsage(VESDataType):
    """memoryUsage datatype"""

    def __init__(self, identifier):
        self.memory_buffered = None
        self.memory_cached = None
        self.memory_configured = None
        self.memory_free = None
        self.memory_slab_recl = None
        self.memory_slab_unrecl = None
        self.memory_used = None
        self.vm_identifier = identifier

    def __str__(self):
        """ for debug purposes """
        return 'vm_identifier : {vm_identifier}\nbuffered : {buffered}\n' \
               'cached : {cached}\nconfigured : {configured}\nfree : {free}\n' \
               'slab_recl : {slab_recl}\nslab_unrecl : {slab_unrecl}\n' \
               'used : {used}\n'.format(buffered=self.memory_buffered,
                                        cached=self.memory_cached, configured=self.memory_configured,
                                        free=self.memory_free, slab_recl=self.memory_slab_recl,
                                        slab_unrecl=self.memory_slab_unrecl, used=self.memory_used,
                                        vm_identifier=self.vm_identifier)

    def get_memory_free(self):
        if self.memory_free is None:
            # calculate the free memory
            if None not in (self.memory_configured, self.memory_used):
                return self.memory_configured - self.memory_used
            else:
                # required field, so return zero
                return 0
        else:
            return self.memory_free

    def get_memory_used(self):
        if self.memory_used is None:
            # calculate the memory used
            if None not in (self.memory_configured, self.memory_free, self.memory_buffered,
                            self.memory_cached, self.memory_slab_recl, self.memory_slab_unrecl):
                return self.memory_configured - (self.memory_free +
                                                 self.memory_buffered + self.memory_cached +
                                                 self.memory_slab_recl + self.memory_slab_unrecl)
            else:
                # required field, so return zero
                return 0
        else:
            return self.memory_used

    def get_memory_total(self):
        if self.memory_configured is None:
            # calculate the total memory
            if None not in (self.memory_used, self.memory_free, self.memory_buffered,
                            self.memory_cached, self.memory_slab_recl, self.memory_slab_unrecl):
                return (self.memory_used + self.memory_free +
                        self.memory_buffered + self.memory_cached +
                        self.memory_slab_recl + self.memory_slab_unrecl)
            else:
                return None
        else:
            return self.memory_configured

    def get_obj(self):
        obj = {
            # required fields
            'memoryFree': self.get_memory_free(),
            'memoryUsed': self.get_memory_used(),
            'vmIdentifier': self.vm_identifier
        }
        # optional fields
        self.set_optional(obj, 'memoryBuffered', self.memory_buffered)
        self.set_optional(obj, 'memoryCached', self.memory_cached)
        self.set_optional(obj, 'memoryConfigured', self.memory_configured)
        self.set_optional(obj, 'memorySlabRecl', self.memory_slab_recl)
        self.set_optional(obj, 'memorySlabUnrecl', self.memory_slab_unrecl)
        return obj


class MeasurementsForVfScaling(Event):
    """MeasurementsForVfScaling datatype"""

    def __init__(self, event_id):
        """Construct the header"""
        super(MeasurementsForVfScaling, self).__init__()
        # common attributes
        self.domain = "measurementsForVfScaling"
        self.event_type = 'hostOS'
        self.event_id = event_id
        # measurement attributes
        self.additional_measurements = []
        self.codec_usage_array = []
        self.concurrent_sessions = 0
        self.configured_entities = 0
        self.cpu_usage_array = []
        self.feature_usage_array = []
        self.filesystem_usage_array = []
        self.latency_distribution = []
        self.mean_request_latency = 0
        self.measurement_interval = 0
        self.number_of_media_ports_in_use = 0
        self.request_rate = 0
        self.vnfc_scaling_metric = 0
        self.additional_fields = []
        self.additional_objects = []
        self.disk_usage_array = []
        self.measurements_for_vf_scaling_version = 2.0
        self.memory_usage_array = []
        self.v_nic_performance_array = []

    def add_additional_measurement(self, named_array):
        self.additional_measurements.append(named_array.get_obj())

    def add_additional_fields(self, field):
        self.additional_fields.append(field.get_obj())

    def add_memory_usage(self, mem_usage):
        self.memory_usage_array.append(mem_usage.get_obj())

    def add_cpu_usage(self, cpu_usage):
        self.cpu_usage_array.append(cpu_usage.get_obj())

    def add_v_nic_performance(self, nic_performance):
        self.v_nic_performance_array.append(nic_performance.get_obj())

    def add_disk_usage(self, disk_usage):
        self.disk_usage_array.append(disk_usage.get_obj())

    def get_obj(self):
        """Get the object of the datatype"""
        obj = {}
        obj['additionalMeasurements'] = self.additional_measurements
        obj['codecUsageArray'] = self.codec_usage_array
        obj['concurrentSessions'] = self.concurrent_sessions
        obj['configuredEntities'] = self.configured_entities
        obj['cpuUsageArray'] = self.cpu_usage_array
        obj['featureUsageArray'] = self.feature_usage_array
        obj['filesystemUsageArray'] = self.filesystem_usage_array
        obj['latencyDistribution'] = self.latency_distribution
        obj['meanRequestLatency'] = self.mean_request_latency
        obj['measurementInterval'] = self.measurement_interval
        obj['numberOfMediaPortsInUse'] = self.number_of_media_ports_in_use
        obj['requestRate'] = self.request_rate
        obj['vnfcScalingMetric'] = self.vnfc_scaling_metric
        obj['additionalFields'] = self.additional_fields
        obj['additionalObjects'] = self.additional_objects
        obj['diskUsageArray'] = self.disk_usage_array
        obj['measurementsForVfScalingVersion'] = self.measurements_for_vf_scaling_version
        obj['memoryUsageArray'] = self.memory_usage_array
        obj['vNicPerformanceArray'] = self.v_nic_performance_array
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
        self.event_category = ""

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
        obj['eventCategory'] = self.event_category
        return obj


class VESPlugin(object):
    """VES plugin with collectd callbacks"""

    def __init__(self):
        """Plugin initialization"""
        self.__plugin_data_cache = {
            'cpu': {'interval': 0.0, 'vls': []},
            'virt': {'interval': 0.0, 'vls': []},
            'disk': {'interval': 0.0, 'vls': []},
            'interface': {'interval': 0.0, 'vls': []},
            'memory': {'interval': 0.0, 'vls': []}
        }
        self.__plugin_config = {
            'Domain': '127.0.0.1',
            'Port': 30000,
            'Path': '',
            'Username': '',
            'Password': '',
            'Topic': '',
            'UseHttps': False,
            'SendEventInterval': 20.0,
            'FunctionalRole': 'Collectd VES Agent',
            'ApiVersion': 5.1,
            'KafkaPort': 9092,
            'KafkaBroker': 'localhost'
        }
        self.__host_name = None
        self.__ves_timer = None
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
        self.__ves_timer = Timer(self.__plugin_config['SendEventInterval'], self.__on_time)
        self.__ves_timer.start()

    def stop_timer(self):
        """Stop event timer"""
        self.__ves_timer.cancel()

    def __on_time(self):
        """Timer thread"""
        self.event_timer()
        self.start_timer()

    def event_send(self, event):
        """Send event to VES"""
        server_url = "http{}://{}:{}{}/eventListener/v{}{}".format(
            's' if self.__plugin_config['UseHttps'] else '', self.__plugin_config['Domain'],
            int(self.__plugin_config['Port']), '{}'.format(
                '/{}'.format(self.__plugin_config['Path']) if (len(self.__plugin_config['Path']) > 0) else ''),
            int(self.__plugin_config['ApiVersion']), '{}'.format(
                '/{}'.format(self.__plugin_config['Topic']) if (len(self.__plugin_config['Topic']) > 0) else ''))
        logging.info('Vendor Event Listener is at: {}'.format(server_url))
        credentials = base64.b64encode('{}:{}'.format(
            self.__plugin_config['Username'], self.__plugin_config['Password']).encode()).decode()
        logging.info('Authentication credentials are: {}'.format(credentials))
        try:
            request = url.Request(server_url)
            request.add_header('Authorization', 'Basic {}'.format(credentials))
            request.add_header('Content-Type', 'application/json')
            logging.debug("Sending {} to {}".format(event.get_json(), server_url))
            vel = url.urlopen(request, event.get_json(), timeout=1)
            logging.debug("Sent data to {} successfully".format(server_url))
        except url.HTTPError as e:
            logging.error('Vendor Event Listener exception: {}'.format(e))
        except url.URLError as e:
            logging.error('Vendor Event Listener is is not reachable: {}'.format(e))
        except Exception as e:
            logging.error('Vendor Event Listener error: {}'.format(e))

    def bytes_to_kb(self, bytes):
        """Convert bytes to kibibytes"""
        return round((bytes / 1024.0), 3)

    def get_hostname(self):
        return socket.gethostname()

    def send_host_measurements(self):
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
                    logging.warning("%s" % vm_value)
                    us_up_to_date = False
                    break
            if not us_up_to_date:
                # one of the cache value is not up-to-date, break
                logging.warning("virt collectd cache values are not up-to-date for {}".format(vm_name))
                continue
            # values are up-to-date, create an event message
            measurement = MeasurementsForVfScaling(self.get_event_id())
            measurement.functional_role = self.__plugin_config['FunctionalRole']
            # fill out reporting_entity
            measurement.reporting_entity_id = self.get_hostname()
            measurement.reporting_entity_name = measurement.reporting_entity_id
            # set source as a host value
            measurement.source_id = vm_name
            measurement.source_name = measurement.source_id
            # fill out EpochMicrosec (convert to us)
            measurement.start_epoch_microsec = (virt_vcpu_total[0]['time'] * 1000000)
            # plugin interval
            measurement.measurement_interval = self.__plugin_data_cache['virt']['interval']
            # memoryUsage
            mem_usage = MemoryUsage(vm_name)
            memory_total = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                type_name='memory', type_instance='total')
            memory_unused = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                 type_name='memory', type_instance='unused')
            memory_rss = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                              type_name='memory', type_instance='rss')
            if len(memory_total) > 0:
                mem_usage.memory_configured = self.bytes_to_kb(memory_total[0]['values'][0])
            if len(memory_unused) > 0:
                mem_usage.memory_free = self.bytes_to_kb(memory_unused[0]['values'][0])
            elif len(memory_rss) > 0:
                mem_usage.memory_free = self.bytes_to_kb(memory_rss[0]['values'][0])
            # since, "used" metric is not provided by virt plugn, set the rest of the memory stats
            # to zero to calculate used based on provided stats only
            mem_usage.memory_buffered = mem_usage.memory_cached = mem_usage.memory_slab_recl = \
                mem_usage.memory_slab_unrecl = 0
            measurement.add_memory_usage(mem_usage)
            # cpuUsage
            virt_vcpus = self.cache_get_value(plugin_instance=vm_name,
                                              plugin_name='virt', type_name='virt_vcpu')
            for virt_vcpu in virt_vcpus:
                cpu_usage = CpuUsage(virt_vcpu['type_instance'])
                cpu_usage.percent_usage = self.cpu_ns_to_percentage(virt_vcpu)
                measurement.add_cpu_usage(cpu_usage)
            # vNicPerformance
            if_packets = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                              type_name='if_packets', mark_as_read=False)
            if_names = [x['type_instance'] for x in if_packets]
            for if_name in if_names:
                if_packets = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                  type_name='if_packets', type_instance=if_name)
                if_octets = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                 type_name='if_octets', type_instance=if_name)
                if_errors = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                 type_name='if_errors', type_instance=if_name)
                if_dropped = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                  type_name='if_dropped', type_instance=if_name)
                v_nic_performance = VNicPerformance(if_name)
                v_nic_performance.received_total_packets_accumulated = if_packets[0]['values'][0]
                v_nic_performance.transmitted_total_packets_accumulated = if_packets[0]['values'][1]
                v_nic_performance.received_octets_accumulated = if_octets[0]['values'][0]
                v_nic_performance.transmitted_octets_accumulated = if_octets[0]['values'][1]
                v_nic_performance.received_error_packets_accumulated = if_errors[0]['values'][0]
                v_nic_performance.transmitted_error_packets_accumulated = if_errors[0]['values'][1]
                v_nic_performance.received_discarded_packets_accumulated = if_dropped[0]['values'][0]
                v_nic_performance.transmitted_discarded_packets_accumulated = if_dropped[0]['values'][1]
                measurement.add_v_nic_performance(v_nic_performance)
            # diskUsage
            disk_octets = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                               type_name='disk_octets', mark_as_read=False)
            disk_names = [x['type_instance'] for x in disk_octets]
            for disk_name in disk_names:
                disk_octets = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                   type_name='disk_octets', type_instance=disk_name)
                disk_ops = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                                type_name='disk_ops', type_instance=disk_name)
                disk_usage = DiskUsage(disk_name)
                disk_usage.disk_octets_read_last = disk_octets[0]['values'][0]
                disk_usage.disk_octets_write_last = disk_octets[0]['values'][1]
                disk_usage.disk_ops_read_last = disk_ops[0]['values'][0]
                disk_usage.disk_ops_write_last = disk_ops[0]['values'][1]
                measurement.add_disk_usage(disk_usage)
            # add additional measurements (perf)
            perf_values = self.cache_get_value(plugin_instance=vm_name, plugin_name='virt',
                                               type_name='perf')
            named_array = NamedArrayOfFields('perf')
            for perf in perf_values:
                named_array.add(Field(perf['type_instance'], str(perf['values'][0])))
            measurement.add_additional_measurement(named_array)
            # add host values as additional measurements
            self.set_additional_fields(measurement, exclude_plugins=['virt'])
            # send event to the VES
            self.event_send(measurement)
        if len(vm_names) > 0:
            # mark the additional measurements metrics as read
            self.mark_cache_values_as_read(exclude_plugins=['virt'])

    def event_timer(self):
        """Event timer thread"""
        self.lock()
        try:
            self.send_host_measurements()
        finally:
            self.unlock()

    def mark_cache_values_as_read(self, exclude_plugins=None):
        """mark the cache values as read"""
        for plugin_name in self.__plugin_data_cache.keys():
            if (exclude_plugins != None and plugin_name in exclude_plugins):
                # skip excluded plugins
                continue;
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                val['updated'] = False

    def set_additional_measurements(self, measurement, exclude_plugins=None):
        """Set addition measurement filed with host/guets values"""
        # add host/guest values as additional measurements
        for plugin_name in self.__plugin_data_cache.keys():
            if (exclude_plugins != None and plugin_name in exclude_plugins):
                # skip excluded plugins
                continue;
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                if val['updated']:
                    array_name = self.make_dash_string(plugin_name, val['plugin_instance'],
                                                       val['type_instance'])
                    named_array = NamedArrayOfFields(array_name)

                    for index in range(len(val['dsnames'])):
                        mname = '{}-{}'.format(val['type'], val['dsnames'][index])
                        named_array.add(Field(mname, str(val['values'][index])))
                    measurement.add_additional_measurement(named_array);
                    val['updated'] = False

    def set_additional_fields(self, measurement, exclude_plugins=None):
        # set host values as additional fields
        for plugin_name in self.__plugin_data_cache.keys():
            if (exclude_plugins != None and plugin_name in exclude_plugins):
                # skip excluded plugins
                continue;
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                if val['updated']:
                    name_prefix = self.make_dash_string(plugin_name, val['plugin_instance'],
                                                        val['type_instance'])

                    for index in range(len(val['dsnames'])):
                        field_name = self.make_dash_string(name_prefix, val['type'], val['dsnames'][index])
                        measurement.add_additional_fields(Field(field_name, str(val['values'][index])))

    def cpu_ns_to_percentage(self, vl):
        """Convert CPU usage ns to CPU %"""
        total = vl['values'][0]
        total_time = vl['time']
        pre_total = vl['pre_values'][0]
        pre_total_time = vl['pre_time']
        if (total_time - pre_total_time) == 0:
            # return zero usage if time diff is zero
            return 0.0
        percent = (100.0 * (total - pre_total)) / ((total_time - pre_total_time) * 1000000000.0)
        logging.debug("pre_time={}, pre_value={}, time={}, value={}, cpu={}%".format(
            pre_total_time, pre_total, total_time, total, round(percent, 2)))
        return round(percent, 2)

    def make_dash_string(self, *args):
        """Join non empty strings with dash symbol"""
        return '-'.join(filter(lambda x: len(x) > 0, args))

    def config(self, config):
        """VES option configuration"""
        for key, value in config.items('config'):
            if key in self.__plugin_config:
                try:
                    if type(self.__plugin_config[key]) == int:
                        value = int(value)
                    elif type(self.__plugin_config[key]) == float:
                        value = float(value)
                    elif type(self.__plugin_config[key]) == bool:
                        value = bool(distutils.util.strtobool(value))

                    if isinstance(value, type(self.__plugin_config[key])):
                        self.__plugin_config[key] = value
                    else:
                        logging.error("Type mismatch with %s" % key)
                        sys.exit()
                except ValueError:
                    logging.error("Incorrect value type for %s" % key)
                    sys.exit()
            else:
                logging.error("Incorrect key configuration %s" % key)
                sys.exit()

    def init(self):
        """Initialisation"""
        # start the VES timer
        self.start_timer()

    def update_cache_value(self, kafka_data):
        """Update value internal collectd cache values or create new one
         Please note, the cache should be locked before using this function"""
        found = False
        if kafka_data['plugin'] not in self.__plugin_data_cache:
            self.__plugin_data_cache[kafka_data['plugin']] = {'vls': []}
        plugin_vl = self.__plugin_data_cache[kafka_data['plugin']]['vls']

        for index in range(len(plugin_vl)):
            # record found, so just update time the values
            if (plugin_vl[index]['plugin_instance'] == kafka_data['plugin_instance']) and \
                    (plugin_vl[index]['type_instance'] == kafka_data['type_instance']) and \
                    (plugin_vl[index]['type'] == kafka_data['type']):
                plugin_vl[index]['pre_time'] = plugin_vl[index]['time']
                plugin_vl[index]['time'] = kafka_data['time']
                plugin_vl[index]['pre_values'] = plugin_vl[index]['values']
                plugin_vl[index]['values'] = kafka_data['values']
                plugin_vl[index]['dsnames'] = kafka_data['dsnames']
                plugin_vl[index]['updated'] = True
                found = True
                break
        if not found:
            value = {}
            # create new cache record
            value['plugin_instance'] = kafka_data['plugin_instance']
            value['type_instance'] = kafka_data['type_instance']
            value['values'] = kafka_data['values']
            value['pre_values'] = kafka_data['values']
            value['type'] = kafka_data['type']
            value['time'] = kafka_data['time']
            value['pre_time'] = kafka_data['time']
            value['host'] = kafka_data['host']
            value['dsnames'] = kafka_data['dsnames']
            value['updated'] = True
            self.__plugin_data_cache[kafka_data['plugin']]['vls'].append(value)
            # update plugin interval based on one received in the value
            self.__plugin_data_cache[kafka_data['plugin']]['interval'] = kafka_data['interval']

    def cache_get_value(self, plugin_name=None, plugin_instance=None,
                        type_name=None, type_instance=None, type_names=None, mark_as_read=True):
        """Get cache value by given criteria"""
        ret_list = []
        if plugin_name in self.__plugin_data_cache:
            for val in self.__plugin_data_cache[plugin_name]['vls']:
                if (type_name == None or type_name == val['type']) and \
                        (plugin_instance == None or plugin_instance == val['plugin_instance']) and \
                        (type_instance == None or type_instance == val['type_instance']) and \
                        (type_names == None or val['type'] in type_names):
                    if mark_as_read:
                        val['updated'] = False
                    ret_list.append(val)
        return ret_list

    def shutdown(self):
        """Shutdown method for clean up"""
        self.stop_timer()

    def run(self):
        """Consumer JSON data from kafka broker"""
        kafka_server = '%s:%s' % (self.__plugin_config.get('KafkaBroker'), self.__plugin_config.get('KafkaPort'))
        consumer = KafkaConsumer('collectd', bootstrap_servers=kafka_server, auto_offset_reset='latest',
                                 enable_auto_commit=False,
                                 value_deserializer=lambda m: json.loads(m.decode('ascii')))

        for message in consumer:
            for kafka_data in message.value:
                self.lock()
                try:
                    # Receive Kafka data and update cache values
                    self.update_cache_value(kafka_data)

                finally:
                    self.unlock()


def main():
    # Parsing cmdline options
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="configfile", default=None, help="Specify config file", metavar="FILE")
    parser.add_argument("--loglevel", dest="level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='WARNING',
                        help="Specify log level (default: %(default)s)", metavar="LEVEL")
    parser.add_argument("--logfile", dest="logfile", default='ves_app.log',
                        help="Specify log file (default: %(default)s)", metavar="FILE")
    args = parser.parse_args()

    # Create log file
    logging.basicConfig(filename=args.logfile, format='%(asctime)s %(message)s', level=args.level)

    # Create Plugin Instance
    plugin_instance = VESPlugin()

    # Read from config file
    if args.configfile:
        config = ConfigParser.ConfigParser()
        config.optionxform = lambda option: option
        config.read(args.configfile)
        # Write Config Values
        plugin_instance.config(config)
    else:
        logging.warning("No configfile specified, using default options")

    # Start timer for interval
    plugin_instance.init()

    # Read Data from Kakfa
    try:
        # Kafka consumer & update cache
        plugin_instance.run()
    except KeyboardInterrupt:
        logging.info(" - Ctrl-C handled, exiting gracefully")
        plugin_instance.shutdown()
        sys.exit()
    except:
        logging.error("Unknown Error")


if __name__ == '__main__':
    main()
