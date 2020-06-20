import subprocess
import time
import urllib


def init_collectd(conf_file_path):
    status, out = subprocess.getstatusoutput(
        "/opt/collectd/sbin/collectd -C {} -T".format(conf_file_path)
    )

    return out


def test_normal_plugin_load():
    output = init_collectd("capabilities_conf/capabilities.conf")

    exp = """plugin "capabilities" successfully loaded"""

    assert exp in output


def test_load_plugin_warning():
    output = init_collectd("capabilities_conf/no_loadplugin.conf")

    exp = """the plugin isn't loaded"""

    assert exp in output
