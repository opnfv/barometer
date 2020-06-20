import subprocess32 as subprocess
import time
import urllib
import commands


def init_collectd(conf_file_path):
    proc = subprocess.Popen(
        ["/opt/collectd/sbin/collectd", "-C", conf_file_path, "-T"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate()
    if out:
        return out
    return err


def test_normal_plugin_load():
    output = init_collectd("capabilities_conf/capabilities.conf")

    exp = """plugin "capabilities" successfully loaded"""

    assert exp in output


def test_load_plugin_warning():
    output = init_collectd("capabilities_conf/no_loadplugin.conf")

    exp = """the plugin isn't loaded"""

    assert exp in output
