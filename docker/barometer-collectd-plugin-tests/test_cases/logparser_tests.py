"Testcases for the logparser plugin"
from os import name
import subprocess
import time
#import shelex

"load plugin that is in the plugin tests folder for any test"
def load_plugin(name=str):
    proc = subprocess.Popen(["/opt/collectd/sbin/collectd", "-C", "$" +"/plugin_configs/"+name+".conf", "-T"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        )
    return proc.communicate()

"assess the if the config of the plugin was loaded"
def test_load_plugin(name=str):
    out, err = load_plugin(name)
    if out:
        return str(out), "PASSED"
    return str(err), "FAIL"

#TODO: add the rest of the tests
def test_pice_notification():
    return True

def test_all_logparser():
    test_pice_notification()
