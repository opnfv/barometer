import subprocess32 as subprocess
import time
import urllib
import commands

import json


def init_collectd():
    proc = subprocess.Popen(
        ["/opt/collectd/sbin/collectd", "-f"], bufsize=0, stdout=subprocess.PIPE
    )
    return proc


def stop_collectd(proc):
    proc.terminate()
    try:
        outs, _ = proc.communicate(timeout=5)
        print("== subprocess exited with rc =", proc.returncode)
        # print(outs.decode('utf-8'))
    except subprocess.TimeoutExpired:
        proc.kill()
        print("subprocess did not terminate in time")


def test_basic_output():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        assert b"BIOS" in resp.read()
    except Exception as e:
        assert True == False


def test_all_dmi_types_present():
    try:
        # status, output = commands.getstatusoutput("curl localhost:9564 | jq ")
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        assert "BIOS" in output  # 0
        assert "SYSTEM" in output  # 1
        assert "BASEBOARD" in output  # 2
        assert "PROCESSORS" in output  # 4
        assert "CACHE" in output  # 7
        assert "PHYSICAL MEMORY ARRAYS" in output  # 16
        assert "MEMORY DEVICES" in output  # 17
        assert "IPMI DEVICE" in output  # 38
        assert "ONBOARD DEVICES EXTENDED INFORMATION" in output  # 41

    except Exception as e:
        assert True == False


def test_bios_data():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput("dmidecode | awk '/type 2,/,/^$/'")

        assert status is 0
        assert output["BIOS"][0]["BIOS Information"]["Vendor"] in dmioutput

    except Exception as e:
        assert True == False


def test_system_information():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput("dmidecode | awk '/type 1,/,/^$/'")

        assert status is 0

        for item in output["SYSTEM"]:
            for k, v in item["System Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_baseboard_information():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput("dmidecode | awk '/type 2,/,/^$/'")

        assert status is 0

        for item in output["BASEBOARD"]:
            for k, v in item["Base Board Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_processor_information():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput("dmidecode | awk '/type 4,/,/^$/'")

        assert status is 0

        for item in output["PROCESSORS"]:
            for k, v in item["Processor Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_cache_information():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput("dmidecode | awk '/type 7,/,/^$/'")

        assert status is 0

        for item in output["CACHE"]:
            for k, v in item["Cache Information"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_physical_memory():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput(
            "dmidecode | awk '/type 16,/,/^$/'"
        )

        assert status is 0

        for item in output["PHYSICAL MEMORY ARRAYS"]:
            for k, v in item["Physical Memory Array"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_memory_device():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput(
            "dmidecode | awk '/type 17,/,/^$/'"
        )

        assert status is 0

        for item in output["MEMORY DEVICES"]:
            for k, v in item["Memory Device"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def test_impi():
    # TODO - Add IMPI test
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput(
            "dmidecode | awk '/type 38,/,/^$/'"
        )

        assert status is 0

    except Exception as e:
        assert True == False


def test_onboard_device_extended_information():
    try:
        resp = urllib.urlopen("http://localhost:9564")
        output = json.load(resp)

        status, dmioutput = commands.getstatusoutput(
            "dmidecode | awk '/type 41,/,/^$/'"
        )

        assert status is 0

        for item in output["ONBOARD DEVICES EXTENDED INFORMATION"]:
            for k, v in item["Onboard Device"].items():
                if isinstance(v, list):
                    for val in v:
                        val in dmioutput
                else:
                    assert v in dmioutput

    except Exception as e:
        assert True == False


def run_capabilities_tests(proc):
    test_basic_output()
    test_all_dmi_types_present()
    test_bios_data()
    test_system_information()
    test_baseboard_information()
    test_processor_information()
    test_cache_information()
    test_physical_memory()
    test_memory_device()
    test_impi()
    test_onboard_device_extended_information()


if __name__ == "__main__":
    proc = init_collectd()

    try:
        time.sleep(4)
        run_capabilities_tests(proc)

    finally:
        stop_collectd(proc)
