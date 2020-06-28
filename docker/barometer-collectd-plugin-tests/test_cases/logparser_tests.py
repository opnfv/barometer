"Testcases for the logparser plugin"
import os 
import subprocess
import warnings
import re

"load plugin that is in the plugin tests folder for any test"
def load_plugin(name=str):
    proc = subprocess.Popen(["/opt/collectd/sbin/collectd", "-C", "$PWD" +"/plugin_configs/"+name+".conf", "-T"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        )
    out, err = proc.communicate()
    if out:
        return out
    
    return err

"assess the if the config of the plugin was loaded"
def test_load_plugin(name=str):
    output = load_plugin(name)
    exp =str('plugin "'+name+'" successfully loaded').encode()
    assert exp in output
    

#TODO: add the rest of the tests
def test_pice_notification():
    warnings.warn("warning: test warning")
    log = open("/var/log/syslog","r+")
    print(log.read())
    return True

def test_all_logparser():
    subprocess.Popen(["/opt/collectd/sbin/collectd", "-C", "$PWD" +"/plugin_configs/logparser.conf", "-T"], bufsize=0, stdout=subprocess.PIPE)
    test_pice_notification()

