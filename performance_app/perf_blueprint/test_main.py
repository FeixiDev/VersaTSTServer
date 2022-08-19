# coding:utf-8
'''
Created on 2022/5/1
@author: Fred
@performance: data
'''

#fromaflask import Flask, jsonify, render_template, request, make_response, views
import kraken.kraken.sshv.utils as utils
from kraken.sshv import log as log
from performance_exc import test_getconfig
from performance_exc import test_databse
from kraken.storage import spoc_yaml_config
from kraken.storage import database_reliability
import kraken.kraken.spof_scenarios.setup as spof_scenarios
import sys
import os
import yaml



def main():
    err = False
    utils._init()
    logger = log.Log()
    utils.set_logger(logger)
    config_list = ["22","1","2","1"]

    cfg = sys.path[0] + '/kraken/config/config_spof.yaml'
    print('cfggggggggggggg',cfg)
    with open(cfg, "r") as f:
        config = yaml.full_load(f)
        chaos_scenarios = config["kraken"].get("chaos_scenarios", [])
        for scenario in chaos_scenarios:
            scenario_type = list(scenario.keys())[0]
            scenarios_list = scenario[scenario_type]
            print(scenarios_list)
            err = spof_scenarios.run(scenarios_list,config_list)
        print('run spof scenario successsssssssssss')
        exit(1)
        if err:
            result = "0"
        else:
            result = "1"
        return 1


if __name__ == "__main__":
    main()


