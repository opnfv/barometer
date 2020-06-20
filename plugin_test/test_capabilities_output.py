import subprocess
import time
from urllib.request import urlopen

import json


def init_collectd():
    proc = subprocess.Popen(
        [
            "/opt/collectd/sbin/collectd",
            "-C",
            "capabilities_conf/capabilities.conf",
            "-f",
        ],
        bufsize=0,
        stdout=subprocess.PIPE,
    )

    return proc


def stop_collectd(proc):
    proc.terminate()
    try:
        outs, _ = proc.communicate(timeout=5)
        print ("== subprocess exited with rc =", proc.returncode)
        # print(outs.decode('utf-8'))
    except subprocess.TimeoutExpired:
        proc.kill()
        print ("subprocess did not terminate in time")


class TestCapabilitiesOutPutClass:
    proc = None

    @classmethod
    def setup_class(cls):
        print("starting collectd")
        cls.proc = init_collectd()
        time.sleep(4)

    @classmethod
    def teardown_class(cls):
        print("killing collectd")
        stop_collectd(cls.proc)

    def test_basic_output(self):
        resp = urlopen("http://localhost:9564")
        assert b"BIOS" in resp.read()

    def test_all_dmi_types_present(self):
        # status, output = commands.getstatusoutput("curl localhost:9564 | jq ")
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        info_list = [
            "BIOS",
            "SYSTEM",
            "BASEBOARD",
            "PROCESSORS",
            "CACHE",
            "PHYSICAL MEMORY ARRAYS",
            "MEMORY DEVICES",
            "IPMI DEVICE",
            "ONBOARD DEVICES EXTENDED INFORMATION",
        ]

        for info in info_list:
            assert info in output, "{} not present".format(info)

    def test_bios_data(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput("dmidecode | awk '/type 0,/,/^$/'")

        assert status is 0

        for item in output["BIOS"]:
            for k, v in item["BIOS Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in BIOS Information".format(v)

    def test_system_information(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput("dmidecode | awk '/type 1,/,/^$/'")

        assert status is 0

        for item in output["SYSTEM"]:
            for k, v in item["System Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in System Information".format(v)

    def test_baseboard_information(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput("dmidecode | awk '/type 2,/,/^$/'")

        assert status is 0

        for item in output["BASEBOARD"]:
            for k, v in item["Base Board Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in Base Board Information".format(v)

    def test_processor_information(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput("dmidecode | awk '/type 4,/,/^$/'")

        assert status is 0

        for item in output["PROCESSORS"]:
            for k, v in item["Processor Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in Processor Information".format(v)

    def test_cache_information(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput("dmidecode | awk '/type 7,/,/^$/'")

        assert status is 0

        for item in output["CACHE"]:
            for k, v in item["Cache Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in Cache Information".format(v)

    def test_physical_memory(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput(
            "dmidecode | awk '/type 16,/,/^$/'"
        )

        assert status is 0

        for item in output["PHYSICAL MEMORY ARRAYS"]:
            for k, v in item["Physical Memory Array"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in Physical Memory Array".format(v)

    def test_memory_device(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput(
            "dmidecode | awk '/type 17,/,/^$/'"
        )

        assert status is 0

        for item in output["MEMORY DEVICES"]:
            for k, v in item["Memory Device"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput, "{} not in Memory Device Information".format(
                        v
                    )

    def test_impi(self):
        # TODO - Add IMPI test
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput(
            "dmidecode | awk '/type 38,/,/^$/'"
        )

        assert status is 0

    def test_onboard_device_extended_information(self):
        resp = urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = subprocess.getstatusoutput(
            "dmidecode | awk '/type 41,/,/^$/'"
        )

        assert status is 0

        for item in output["ONBOARD DEVICES EXTENDED INFORMATION"]:
            for k, v in item["Onboard Device"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert (
                        v in dmioutput
                    ), "{} not in Onboard Device Information".format(v)


