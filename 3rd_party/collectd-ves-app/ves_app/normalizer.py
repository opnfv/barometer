#
# Copyright(c) 2017 Intel Corporation. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
#   Volodymyr Mytnyk <volodymyrx.mytnyk@intel.com>
#

from . import yaml
import logging
import datetime
import time
from threading import RLock
from threading import Timer
from threading import Thread
import re

# import YAML loader
try:
    from .yaml import CLoader as Loader
except ImportError:
    from .yaml import Loader

# import synchronized queue
import queue


class Config(object):
    """Configuration class used to pass config option into YAML file"""

    def __init__(self, interval):
        self.interval = interval


class System(object):
    """System class which provides information like host, time etc., into YAML
    file"""

    def __init__(self):
        self.hostname = 'localhost'
        self._id = 0

    @property
    def id(self):
        self._id = self._id + 1
        return self._id

    @property
    def time(self):
        return time.time()

    @property
    def date(self):
        return datetime.date.today().isoformat()


class ItemIterator(object):
    """Item iterator returned by Collector class"""

    def __init__(self, collector, items):
        """Item iterator init"""
        logging.debug('{}:__init__()'.format(self.__class__.__name__))
        self._items = items
        self._collector = collector
        self._index = 0

    def __next__(self):
        """Returns next item from the list"""
        if self._index == len(self._items):
            raise StopIteration
        curr_index = self._index
        self._index = curr_index + 1
        return self.items[curr_index]

    def __getitem__(self, key):
        """get item by index"""
        return self._items[key]

    def __len__(self):
        """Return length of elements"""
        return len(self._items)

    def __del__(self):
        """Destroy iterator and unlock the collector"""
        logging.debug('{}:__del__()'.format(self.__class__.__name__))
        self._collector.unlock()


class ItemObject(object):
    """Item object returned by Collector class"""

    def __init__(self, collector, hash_):
        """Item object init"""
        logging.debug('{}:__init__()'.format(self.__class__.__name__))
        super(ItemObject, self).__setattr__('_collector', collector)
        super(ItemObject, self).__setattr__('_hash', hash_)

    def __setattr__(self, name, value):
        t, item = self._collector._metrics[self._hash]
        logging.debug('{}:__setattr__(name={}, value={})'.format(
                      self.__class__.__name__, name, value))
        setattr(item, name, value)
        self._collector._metrics[self._hash] = (time.time(), item)

    def __del__(self):
        """Destroy item object and unlock the collector"""
        logging.debug('{}:__del__()'.format(self.__class__.__name__))
        self._collector.unlock()


class Collector(object):
    """Thread-safe collector with aging feature"""

    def __init__(self, age_timeout):
        """Initialization"""
        self._metrics = {}
        self._lock = RLock()
        self._age_timeout = age_timeout
        self._start_age_timer()

    def _start_age_timer(self):
        """Start age timer"""
        self._age_timer = Timer(self._age_timeout, self._on_timer)
        self._age_timer.start()

    def _stop_age_timer(self):
        """Stop age timer"""
        self._age_timer.cancel()

    def _on_timer(self):
        """Age timer"""
        self._start_age_timer()
        self._check_aging()

    def _check_aging(self):
        """Check aging time for all items"""
        self.lock()
        for data_hash, data in list(self._metrics.items()):
            age, item = data
            if ((time.time() - age) >= self._age_timeout):
                # aging time has expired, remove the item from the collector
                logging.debug('{}:_check_aging():value={}'.format(
                              self.__class__.__name__, item))
                self._metrics.pop(data_hash)
                del(item)
        self.unlock()

    def lock(self):
        """Lock the collector"""
        logging.debug('{}:lock()'.format(self.__class__.__name__))
        self._lock.acquire()

    def unlock(self):
        """Unlock the collector"""
        logging.debug('{}:unlock()'.format(self.__class__.__name__))
        self._lock.release()

    def get(self, hash_):
        self.lock()
        if hash_ in self._metrics:
            return ItemObject(self, hash_)
        self.unlock()
        return None

    def add(self, item):
        """Add an item into the collector"""
        self.lock()
        logging.debug('{}:add(item={})'.format(self.__class__.__name__, item))
        self._metrics[hash(item)] = (time.time(), item)
        self.unlock()

    def items(self, select_list=[]):
        """Returns locked (safe) item iterator"""
        metrics = []
        self.lock()
        for k, item in list(self._metrics.items()):
            _, value = item
            for select in select_list:
                if value.match(**select):
                    metrics.append(value)
        return ItemIterator(self, metrics)

    def destroy(self):
        """Destroy the collector"""
        self._stop_age_timer()


class CollectdData(object):
    """Base class for Collectd data"""

    def __init__(self, host=None, plugin=None, plugin_instance=None,
                 type_=None, type_instance=None, time_=None):
        """Class initialization"""
        self.host = host
        self.plugin = plugin
        self.plugin_instance = plugin_instance
        self.type_instance = type_instance
        self.type = type_
        self.time = time_

    @classmethod
    def is_regular_expression(cls, expr):
        return len(expr) > 1 and expr[0] == '/' and expr[-1] == '/'

    def match(self, **kargs):
        # compare the metric
        for key, value in list(kargs.items()):
            if self.is_regular_expression(value):
                if re.match(value[1:-1], getattr(self, key)) is None:
                    return False
            elif value != getattr(self, key):
                return False
        # return match event if kargs is empty
        return True


class CollectdNotification(CollectdData):
    """Collectd notification"""

    def __init__(self, host=None, plugin=None, plugin_instance=None,
                 type_=None, type_instance=None, severity=None, message=None):
        super(CollectdNotification, self).__init__(
            host, plugin, plugin_instance, type_, type_instance)
        self.severity = severity
        self.message = message

    def __repr__(self):
        return '{}(host={}, plugin={}, plugin_instance={}, type={}, ' \
               'type_instance={}, severity={}, message={}, time={})'.format(
                   self.__class__.__name__, self.host, self.plugin,
                   self.plugin_instance, self.type, self.type_instance,
                   self.severity, self.message, time)


class CollectdValue(CollectdData):
    """Collectd value"""

    def __init__(self, host=None, plugin=None, plugin_instance=None,
                 type_=None, type_instance=None, ds_name='value', value=None,
                 interval=None):
        super(CollectdValue, self).__init__(
            host, plugin, plugin_instance, type_, type_instance)
        self.value = value
        self.ds_name = ds_name
        self.interval = interval

    @classmethod
    def hash_gen(cls, host, plugin, plugin_instance, type_,
                 type_instance, ds_name):
        return hash((host, plugin, plugin_instance, type_,
                    type_instance, ds_name))

    def __eq__(self, other):
        return hash(self) == hash(other) and self.value == other.value

    def __hash__(self):
        return self.hash_gen(self.host, self.plugin, self.plugin_instance,
                             self.type, self.type_instance, self.ds_name)

    def __repr__(self):
        return '{}(host={}, plugin={}, plugin_instance={}, type={}, ' \
               'type_instance={}, ds_name={}, value={}, time={})'.format(
                   self.__class__.__name__, self.host, self.plugin,
                   self.plugin_instance, self.type, self.type_instance,
                   self.ds_name, self.value, self.time)


class Item(yaml.YAMLObject):
    """Base class to process tags like ArrayItem/ValueItem"""

    @classmethod
    def format_node(cls, mapping, metric):
        if mapping.tag in [
                'tag:yaml.org,2002:str', Bytes2Kibibytes.yaml_tag,
                Number.yaml_tag, StripExtraDash.yaml_tag]:
            return yaml.ScalarNode(mapping.tag, mapping.value.format(**metric))
        elif mapping.tag == 'tag:yaml.org,2002:map':
            values = []
            for key, value in mapping.value:
                values.append((yaml.ScalarNode(key.tag, key.value),
                              cls.format_node(value, metric)))
            return yaml.MappingNode(mapping.tag, values)
        elif mapping.tag in [ArrayItem.yaml_tag, ValueItem.yaml_tag]:
            values = []
            for seq in mapping.value:
                map_values = list()
                for key, value in seq.value:
                    if key.value == 'SELECT':
                        map_values.append((yaml.ScalarNode(key.tag, key.value),
                                          cls.format_node(value, metric)))
                    else:
                        map_values.append((yaml.ScalarNode(key.tag, key.value),
                                          value))
                values.append(yaml.MappingNode(seq.tag, map_values))
            return yaml.SequenceNode(mapping.tag, values)
        elif mapping.tag in [MapValue.yaml_tag]:
            values = []
            for key, value in mapping.value:
                if key.value == 'VALUE':
                    values.append((yaml.ScalarNode(key.tag, key.value),
                                  cls.format_node(value, metric)))
                else:
                    values.append((yaml.ScalarNode(key.tag, key.value), value))
            return yaml.MappingNode(mapping.tag, values)
        return mapping


class ValueItem(Item):
    """Class to process VlaueItem tag"""
    yaml_tag = '!ValueItem'

    @classmethod
    def from_yaml(cls, loader, node):
        logging.debug('{}:from_yaml(loader={})'.format(cls.__name__, loader))
        default, select, value_desc = None, list(), None
        # find value description
        for elem in node.value:
            for key, value in elem.value:
                if key.value == 'VALUE':
                    assert value_desc is None, "VALUE key already set"
                    value_desc = value
                if key.value == 'SELECT':
                    select.append(loader.construct_mapping(value))
                if key.value == 'DEFAULT':
                    assert default is None, "DEFAULT key already set"
                    default = loader.construct_object(value)
        # if VALUE key isn't given, use default VALUE key
        # format: `VALUE: !Number '{vl.value}'`
        if value_desc is None:
            value_desc = yaml.ScalarNode(tag='!Number', value='{vl.value}')
        # select collectd metric based on SELECT condition
        metrics = loader.collector.items(select)
        assert len(metrics) < 2, \
            'Wrong SELECT condition {}, selected {} metrics'.format(
            select, len(metrics))
        if len(metrics) > 0:
            item = cls.format_node(value_desc, {'vl': metrics[0],
                                   'system': loader.system})
            return loader.construct_object(item)
        # nothing has been found by SELECT condition, set to DEFAULT value.
        assert default is not None, "No metrics selected by SELECT condition" \
            " {} and DEFAULT key isn't set".format(select)
        return default


class ArrayItem(Item):
    """Class to process ArrayItem tag"""
    yaml_tag = '!ArrayItem'

    @classmethod
    def from_yaml(cls, loader, node):
        logging.debug('{}:process(loader={}, node={})'.format(cls.__name__,
                      loader, node))
        # e.g.:
        # SequenceNode(tag=u'!ArrayItem', value=[
        #   MappingNode(tag=u'tag:yaml.org,2002:map', value=[
        #     (ScalarNode(tag=u'tag:yaml.org,2002:str', value=u'SELECT'),
        #       MappingNode(tag=u'tag:yaml.org,2002:map', value=[
        #         (ScalarNode(tag=u'tag:yaml.org,2002:str', value=u'plugin'),
        #           , ...)
        #       ]), ...
        #     ), (key, value), ... ])
        #   , ... ])
        assert isinstance(node, yaml.SequenceNode), \
            "{} tag isn't YAML array".format(cls.__name__)
        select, index_keys, items, item_desc = list(), list(), list(), None
        for elem in node.value:
            for key, value in elem.value:
                if key.value == 'ITEM-DESC':
                    assert item_desc is None, "ITEM-DESC key already set"
                    item_desc = value
                if key.value == 'INDEX-KEY':
                    assert len(index_keys) == 0, "INDEX-KEY key already set"
                    index_keys = loader.construct_sequence(value)
                if key.value == 'SELECT':
                    select.append(loader.construct_mapping(value))
        # validate item description
        assert item_desc is not None, "Mandatory ITEM-DESC key isn't set"
        assert len(select) > 0 or len(index_keys) > 0, \
            "Mandatory key (INDEX-KEY or SELECT) isn't set"
        metrics = loader.collector.items(select)
        # select metrics based on INDEX-KEY provided
        if len(index_keys) > 0:
            metric_set = set()
            for metric in metrics:
                value = CollectdValue()
                for key in index_keys:
                    setattr(value, key, getattr(metric, key))
                metric_set.add(value)
            metrics = list(metric_set)
        # build items based on SELECT and/or INDEX-KEY criteria
        for metric in metrics:
            item = cls.format_node(item_desc,
                                   {'vl': metric, 'system': loader.system,
                                       'config': loader.config})
            items.append(loader.construct_mapping(item))
        return items


class Measurements(ArrayItem):
    """Class to process Measurements tag"""
    yaml_tag = '!Measurements'


class Events(Item):
    """Class to process Events tag"""
    yaml_tag = '!Events'

    @classmethod
    def from_yaml(cls, loader, node):
        condition, item_desc = dict(), None
        for elem in node.value:
            for key, value in elem.value:
                if key.value == 'ITEM-DESC':
                    item_desc = value
                if key.value == 'CONDITION':
                    condition = loader.construct_mapping(value)
        assert item_desc is not None, "Mandatory ITEM-DESC key isn't set"
        if loader.notification.match(**condition):
            item = cls.format_node(item_desc, {
                'n': loader.notification, 'system': loader.system})
            return loader.construct_mapping(item)
        return None


class Bytes2Kibibytes(yaml.YAMLObject):
    """Class to process Bytes2Kibibytes tag"""
    yaml_tag = '!Bytes2Kibibytes'

    @classmethod
    def from_yaml(cls, loader, node):
        return round(float(node.value) / 1024.0, 3)


class Number(yaml.YAMLObject):
    """Class to process Number tag"""
    yaml_tag = '!Number'

    @classmethod
    def from_yaml(cls, loader, node):
        try:
            return int(node.value)
        except ValueError:
            return float(node.value)


class StripExtraDash(yaml.YAMLObject):
    """Class to process StripExtraDash tag"""
    yaml_tag = '!StripExtraDash'

    @classmethod
    def from_yaml(cls, loader, node):
        return '-'.join([x for x in node.value.split('-') if len(x) > 0])


class MapValue(yaml.YAMLObject):
    """Class to process MapValue tag"""
    yaml_tag = '!MapValue'

    @classmethod
    def from_yaml(cls, loader, node):
        mapping, val = None, None
        for key, value in node.value:
            if key.value == 'TO':
                mapping = loader.construct_mapping(value)
            if key.value == 'VALUE':
                val = loader.construct_object(value)
        assert mapping is not None, "Mandatory TO key isn't set"
        assert val is not None, "Mandatory VALUE key isn't set"
        assert val in mapping, \
            'Value "{}" cannot be mapped to any of {} values'.format(
                val, list(mapping.keys()))
        return mapping[val]


class Normalizer(object):
    """Normalization class which handles events and measurements"""

    def __init__(self):
        """Init"""
        self.interval = None
        self.collector = None
        self.system = None
        self.queue = None
        self.timer = None

    @classmethod
    def read_configuration(cls, config_file):
        """read YAML configuration file"""
        # load YAML events/measurements definition
        f = open(config_file, 'r')
        doc_yaml = yaml.compose(f)
        f.close()
        # split events & measurements definitions
        measurements, events = list(), list()
        for key, value in doc_yaml.value:
            if value.tag == Measurements.yaml_tag:
                measurements.append((key, value))
            if value.tag == Events.yaml_tag:
                events.append((key, value))
        measurements_yaml = yaml.MappingNode('tag:yaml.org,2002:map',
                                             measurements)
        measurements_stream = yaml.serialize(measurements_yaml)
        events_yaml = yaml.MappingNode('tag:yaml.org,2002:map', events)
        events_stream = yaml.serialize(events_yaml)
        # return event & measurements definition
        return events_stream, measurements_stream

    def initialize(self, config_file, interval):
        """Initialize the class"""
        e, m = self.read_configuration(config_file)
        self.measurements_stream = m
        self.events_stream = e
        self.system = System()
        self.config = Config(interval)
        self.interval = interval
        # start collector with aging time = double interval
        self.collector = Collector(interval * 2)
        # initialize event thread
        self.queue = queue.Queue()
        self.event_thread = Thread(target=self.event_worker)
        self.event_thread.daemon = True
        self.event_thread.start()
        # initialize measurements timer
        self.start_timer()

    def destroy(self):
        """Destroy the class"""
        self.collector.destroy()
        self.post_event(None)  # send stop event
        self.event_thread.join()
        self.stop_timer()

    def start_timer(self):
        """Start measurements timer"""
        self.timer = Timer(self.interval, self.on_timer)
        self.timer.start()

    def stop_timer(self):
        """Stop measurements timer"""
        self.timer.cancel()

    def on_timer(self):
        """Measurements timer"""
        self.start_timer()
        self.process_measurements()

    def event_worker(self):
        """Event worker"""
        while True:
            event = self.queue.get()
            if isinstance(event, CollectdNotification):
                self.process_notify(event)
                continue
            # exit for the worker
            break

    def get_collector(self):
        """Get metric collector reference"""
        return self.collector

    def process_measurements(self):
        """Process measurements"""
        loader = Loader(self.measurements_stream)
        setattr(loader, 'collector', self.collector)
        setattr(loader, 'system', self.system)
        setattr(loader, 'config', self.config)
        measurements = loader.get_data()
        for measurement_name in measurements:
            logging.debug('Process "{}" measurements: {}'.format(
                measurement_name, measurements[measurement_name]))
            for measurement in measurements[measurement_name]:
                self.send_data(measurement)

    def process_notify(self, notification):
        """Process events"""
        loader = Loader(self.events_stream)
        setattr(loader, 'notification', notification)
        setattr(loader, 'system', self.system)
        notifications = loader.get_data()
        for notify_name in notifications:
            logging.debug('Process "{}" notification'.format(notify_name))
            if notifications[notify_name] is not None:
                self.send_data(notifications[notify_name])

    def send_data(self, data):
        """Send data"""
        assert False, 'send_data() is abstract function and MUST be overridden'

    def post_event(self, notification):
        """Post notification into the queue to process"""
        self.queue.put(notification)
