"runs the test cases for all specified plugins"

#TODO: refactor test_load_plugin to util_test.py
from test_cases.logparser_tests import test_load_plugin
from test_cases.logparser_tests import test_all_logparser


if __name__ == "__main__":
    
    #write all responses to a file
    #results_dir = "/results"

    print(test_load_plugin("logparser"))
    print(test_load_plugin("noload_logparser"))
    print(test_all_logparser())
