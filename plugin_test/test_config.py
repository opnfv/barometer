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

def inject_errors(file=str):
    out = subprocess.run(
        "/tests/logparser_testutils/aer-inject/aer-inject /tests/utils/"+file,
        capture_output=True
        )
    return out

"load plugin that is in the plugin tests folder for any test"
def load_plugin(name=str):
    output = init_conf("configs/"+name+".conf")
    exp = 'plugin "'+name+'" successfully loaded'
    assert exp in output

"assess the if the config of the plugin was loaded"
def noload_plugin(name=str):
    output = init_conf(str("configs/"+name+".conf"))
    exp = "the plugin isn't loaded"
    assert exp in output

def test_pcieError():
    output = inject_errors("AER_test1")
    exp = "pcie_errors"
    assert exp in output

"tests for logparser configs"
def test_configs_logparser():
    load_plugin("logparser")
    noload_plugin("noload_logparser")
