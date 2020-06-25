##############################################################################
# Copyright (c) 2020-21 Anuket and others
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"Testcases for plugin configs"
import os
import subprocess
import warnings
import re


class CollectdTestBase():

    "initialise config & return output"
    @classmethod
    def start_collectd(cls, conf_file_path):
        status, out = subprocess.getstatusoutput(
            "/opt/collectd/sbin/collectd -C {} -T".format(conf_file_path)
        )
        return out


class CollectdTestLogparser(CollectdTestBase):
    "load plugin that is in the plugin tests folder for any test"
    def test_load_plugin(self):
        name = "logparser"
        output = CollectdTestBase.start_collectd("configs/{}.conf".format(name))
        exp = 'plugin "{}" successfully loaded'.format(name)
        assert exp in output


    "assess the if the config of the plugin was loaded"
    def test_noload_plugin(self):
        name = "noload_logparser"
        output = CollectdTestBase.start_collectd("configs/{}.conf".format(name))
        exp = "the plugin isn't loaded"
        assert exp in output


class CollectdTestCapabilities(CollectdTestBase):
    def test_load_plugin(self):
        name = "capabilities-001"
        output = CollectdTestBase.start_collectd("configs/{}.conf".format(name))
        exp = "plugin \"capabilities\" successfully loaded"
        assert exp in output
