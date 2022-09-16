# coding:utf-8
'''
Created on 2022/5/1
@author: Fred
@performance: data
'''

from flask import Flask, jsonify, render_template, request, make_response, views
from kraken.sshv import utils as utils
from kraken.sshv import log as log
#from performance_exc import utils
#from performance_exc import log
from performance_exc import test_getconfig
from performance_exc import test_databse
from kraken.storage import spoc_yaml_config
from kraken.storage import database_reliability
from upload_file_fun import data_processing
import kraken.kraken.spof_scenarios.setup as spof_scenarios
import sys
import os
import yaml



UPLOAD_FOLDER = '../../upload_file_fun'

def cors_data(datadict): #解决跨域问题
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response
 




def get_request_data():
    if request.method == 'GET':
        str_data = request.args.items()
        dict_data = dict(str_data)
        return dict_data





class selfDCreate(views.MethodView):
    def get(self):
        data_all = get_request_data()
        data = eval(data_all['data'])
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        obj_conf = test_getconfig.Get_config_info(data)
        run_count = obj_conf.get_run_count()
        run_count = int(run_count)
        for i in range(run_count):
            obj_test = test_getconfig.Self_defined_scenarios(data)
        return cors_data('SUCCESS')





class seqrwCreate(views.MethodView):
    def get(self):
        data_all = get_request_data()
        data = eval(data_all['data'])
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        obj_conf = test_getconfig.Get_config_info(data)
        run_count = obj_conf.get_run_count()
        run_count = int(run_count)
        for i in range(run_count):
            obj_test = test_getconfig.Seq_rw_scenarios(data)
        return cors_data('SUCCESS')





class videoCreate(views.MethodView):
    def get(self):
        data_all = get_request_data()
        data = eval(data_all['data'])
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        obj_conf = test_getconfig.Get_config_info(data)
        run_count = obj_conf.get_run_count()
        run_count = int(run_count)
        for i in range(run_count):
            obj_test = test_getconfig.Video_scenarios(data)
        return cors_data('SUCCESS')





class randomrwCreate(views.MethodView):
    def get(self):
        data_all = get_request_data()
        data = eval(data_all['data'])
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        obj_conf = test_getconfig.Get_config_info(data)
        run_count = obj_conf.get_run_count()
        run_count = int(run_count)
        for i in range(run_count):
            obj_test = test_getconfig.Random_rw_scenarios(data)
        return cors_data('SUCCESS')

class randomrwCreate1(views.MethodView):
    def get(self):
        return cors_data('SUCCESS')


class spofPvcCreate(views.MethodView):
    def get(self):
        data_all = get_request_data()
        data = eval(data_all['data'])
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        spoc_yaml_config.Handle_pvc_yaml(data,'/kraken/kraken/kubernetes/res_file/pvctest.yaml')
        spoc_yaml_config.Handle_spof_yaml(data,'/kraken/scenarios/spof_pvc_scenario.yaml')
        file_path = sys.path[0] + '/kraken/config/config_spof_pvc.yaml'
        spoc_yaml_config.test_spoc_pvc(file_path)
        return cors_data('SUCCESS')


class spofCreate(views.MethodView):
    def get(self):
        err = 0
        data = get_request_data()
        dict_data = eval(data['data'])
        print('dict_dataaaaaaaaaa',dict_data)
        #logger = log.Log()
        #utils._init()
        #logger = log.Log()
        #utils.set_logger(logger)
        storageClassName = dict_data["storageclass_name"]
        pvc_size = dict_data["pvc_size"]
        kind = dict_data["test_action"]
        runs = dict_data["test_times"]
        config_list = [storageClassName,pvc_size,kind,runs]
        print('config_listttttttttttt',config_list)
        cfg = sys.path[0] + '/kraken/config/config_spof.yaml'
        print('cfggggggggggggg',cfg)
        spoc_yaml_config.Handle_spof_yaml(dict_data,'/kraken/scenarios/spof_scenario.yaml')
        with open(cfg, "r") as f:
            config = yaml.full_load(f)
        print('modify spof yaml')
        chaos_scenarios = config["kraken"].get("chaos_scenarios", [])
        for scenario in chaos_scenarios:
            scenario_type = list(scenario.keys())[0]
            scenarios_list = scenario[scenario_type]
            left_runs,fail_time = spof_scenarios.run(scenarios_list,config_list)
        if left_runs:
            result = "failed"
            utils.prt_log('', "spof scenario not pass, failed at %s !" % fail_time,0)
        else:
            result = "pass"
            utils.prt_log('', "spof scenario pass",0)

        print('1111111111222222222222',)
        spof_yaml = sys.path[0] + '/kraken/scenarios/spof_scenario.yaml'
        with open(spof_yaml, "r") as f:
            spof_pvc_conf = yaml.full_load(f)
        DB_ip = spof_pvc_conf['DB ip']  #new add
        DB_port = int(spof_pvc_conf['DB port'])
        Test_name = spof_pvc_conf['name']
         #new add
        Exact_times = int(runs)-left_runs
        database_reliability.Write_database_reliability(DB_ip,DB_port,'spof_scenarise',kind,result,Exact_times,runs,Test_name)
        print('doneeeeeeeeeeeeeeeeeeee')
        return cors_data(result)






class spofpvcShow(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/kraken/scenarios/spof_pvc_scenario.yaml'
        if os.path.exists(file_path) == True:
            obj_dbinfo=database_reliability.Get_dbinfo_reliability(file_path)
            data = obj_dbinfo.get_info()
        return cors_data(data)



class seqreadShowIOPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/seqrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_iops_data_read()
            return cors_data(data)

class seqreadShowMBPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/seqrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_mbps_data_read()
            return cors_data(data)

class seqwriteShowIOPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/seqrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_iops_data_write()
            return cors_data(data)

class seqwriteShowMBPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/seqrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_mbps_data_write()
            return cors_data(data)




class videoreadShowIOPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/video_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_iops_data_read()
            return cors_data(data)

class videoreadShowMBPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/video_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_mbps_data_read()
            return cors_data(data)

class videowriteShowIOPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/video_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_iops_data_write()
            return cors_data(data)

class videowriteShowMBPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/video_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_mbps_data_write()
            return cors_data(data)





class randomrwShowIOPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/randomrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_iops_data_randrw()
            return cors_data(data)

class randomrwShowMBPS(views.MethodView):
    def get(self):
        file_path = sys.path[0] + '/performance_exc/randomrw_config.txt'
        if os.path.exists(file_path) == True:
            with open(file_path,'r') as f:
                aaa = f.read().splitlines()
                db_ip = aaa[1][6:]
                db_port = int(aaa[2][8:])
                table_name = aaa[0][11:]
            obj_da = test_databse.Get_data_info(db_ip,db_port,table_name)
            data = obj_da.get_mbps_data_randrw()
            return cors_data(data)

class spofScenarioUpload(views.MethodView):
    def get(self):
        if request.method =='POST':
            spof_scenario_yaml = request.files['file']
            if spof_scenario_yaml.filename != '':
                spof_scenario_yaml.save(UPLOAD_FOLDER)
                file_path = sys.path[0] + '/upload_file_fun/spof_scenario.yaml'
                data_processing.UpdateYaml.update_spof_scenario(file_path)
                return cors_data('SUCCESS')

class spofpvcScenarioUpload(views.MethodView):
    def get(self):
        if request.method == 'POST':
            spof_pvc_scenario_yaml = request.files['file']
            if spof_pvc_scenario_yaml.filename != '':
                spof_pvc_scenario_yaml.save(UPLOAD_FOLDER)
                file_path = sys.path[0] + '/upload_file_fun/spof_pvc_scenario.yaml'
                data_processing.UpdateYaml.update_spof_pvc_scenario(file_path)
                return cors_data('SUCCESS')


class selfdefinedScenarioUpload(views.MethodView):
    def get(self):
        if request.method == 'POST':
            self_defined_scenario_yaml = request.files['file']
            if self_defined_scenario_yaml.filename != '':
                self_defined_scenario_yaml.save(UPLOAD_FOLDER)
                return cors_data('SUCCESS')

class videoScenarioUpload(views.MethodView):
    def get(self):
        if request.method == 'POST':
            video_scenario_yaml = request.files['file']
            if video_scenario_yaml.filename != '':
                video_scenario_yaml.save(UPLOAD_FOLDER)
                return cors_data('SUCCESS')

class seqrwScenarioUpload(views.MethodView):
    def get(self):
        if request.method == 'POST':
            Seq_rw_scenario_yaml = request.files['file']
            if Seq_rw_scenario_yaml.filename != '':
                Seq_rw_scenario_yaml.save(UPLOAD_FOLDER)
                return cors_data('SUCCESS')

class randomrwScenarioUpload(views.MethodView):
    def get(self):
        if request.method == 'POST':
            random_rw_scenario_yaml = request.files['file']
            if random_rw_scenario_yaml.filename != '':
                random_rw_scenario_yaml.save(UPLOAD_FOLDER)
                return cors_data('SUCCESS')

