##############################################################################
# Copyright (c) 2017 <Company or Individual> and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"runs the test cases for all specified plugins"

#TODO: refactor test_load_plugin to util_test.py
from test_cases.logparser_tests import test_load_plugin
from test_cases.logparser_tests import test_all_logparser


if __name__ == "__main__":

    print(test_load_plugin("logparser"))
    #print(test_load_plugin("noload_logparser"))
    print(test_all_logparser())
