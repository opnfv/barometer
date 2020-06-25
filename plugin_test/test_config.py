##############################################################################
# Copyright (c) 2020 Intel Corporation and OPNFV.
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

"initialise config & return output"
def init_conf(conf_file_path):
    status, out = subprocess.getstatusoutput(
        "/opt/collectd/sbin/collectd -C {} -T".format(conf_file_path)
    )
    return out


"load plugin that is in the plugin tests folder for any test"
def test_load_plugin():
    name = "logparser"
    output = init_conf("configs/{}.conf".format(name))
    exp = 'plugin "{}" successfully loaded'.format(name)
    assert exp in output


"assess the if the config of the plugin was loaded"
def test_noload_plugin():
    name = "noload_logparser"
    output = init_conf("configs/{}.conf".format(name))
    exp = "the plugin isn't loaded"
    assert exp in output
