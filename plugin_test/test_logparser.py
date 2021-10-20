##############################################################################
# Copyright (c) 2020-21 Anuket and others
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"Plugin specific tests for logparser"
import subprocess
import time
import logging

"initialise the plugin"
def init_collectd():
    proc = subprocess.Popen(
        [
            "/opt/collectd/sbin/collectd",
            "-C",
            "configs/logparser.conf",
            "-f",
        ],
        bufsize=0,
        stdout=subprocess.PIPE,
    )
    return proc

"terminate the proc, in this case use for plugin"
def stop_collectd(proc):
    proc.terminate()
    try:
        outs, _ = proc.communicate(timeout=5)
        print ("== subprocess exited with rc =", proc.returncode)
        # print(outs.decode('utf-8'))
    except subprocess.TimeoutExpired:
        proc.kill()
        print ("subprocess did not terminate in time")


"Class to test collectd, compliant with pytest framework"
class TestCollectd:
    proc = None
    logging.basicConfig(filename="utils/logparser_testlog.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG
                        )
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logging.getLogger("").addHandler(console)


    @classmethod
    def setup_class(cls):
        print("starting collectd")
        cls.proc = init_collectd()

    @classmethod
    def teardown_class(cls):
        print("killing collectd")
        stop_collectd(cls.proc)

    def test_fullread_notification(self):
        pipe = subprocess.Popen(["pwd"], stdout=subprocess.PIPE).stdout
        output = pipe.read()
        assert "test".encode() in output
