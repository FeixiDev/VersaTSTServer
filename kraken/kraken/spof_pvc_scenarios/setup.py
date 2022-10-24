import subprocess
import re
from charset_normalizer import logging
import yaml
import time
import signal
from threading import Thread
from kraken.kraken.kubernetes import client as kubecli
from  kraken.sshv import utils as utils
from kraken.sshv import log as log
from kraken.sshv import control as control
from kraken.linstorclient import client as linstorcli
from kraken.storage import database_reliability
from kraken.sshv import send_email
# from kraken.kraken.spof_pvc_scenarios import test_database_reliability

#import kraken.kubernetes.client as kubecli
#import sshv.utils as utils
#import sshv.log as log
#import sshv.control as control
#from linstorclient import client as linstorcli
#from kraken.spof_pvc_scenarios import test_database_reliability
import sys


STOP_FLAG = None
PVC_ID = 0
NAME_SPACE = "pvctest"

class PVCNumError(Exception):
    pass

class TimeoutExpired(Exception):
    pass

def run(scenarios_list, config):
    global STOP_FLAG
    global PVC_ID

    with open(sys.path[0] + '/kraken/scenarios/spof_pvc_scenario.yaml', 'r', encoding='utf-8') as sps:
        data = yaml.full_load(sps)
        mail_receiver = data.get('mail_receive')

    # 检查 namespace 中是否为空
    # if kubecli.list_pvc(namespace=NAME_SPACE):
    #     logging.error("There already exists pvc, please clear it and try again")
    #     return
        
    # read pvc config
    conf = scenarios_list[0][0]
    # print('111111ccccc',conf)  #spof_pvc_scenario.yaml
    with open(conf, "r") as f:
        spof_pvc_conf = yaml.full_load(f)
    # print('11111111spof_pvc_conf',spof_pvc_conf)  #get spof_pvc_scenario.yaml info
    pvc = spof_pvc_conf['pvc']
    # print('11111111pvc',pvc)  #/kubernetes/res_file/pvctest.yaml
    times = spof_pvc_conf['times']
    # print('11111111times',times)
    Test_action = spof_pvc_conf['kind']  #new add
    Test_name = spof_pvc_conf['name']
    Test_times = spof_pvc_conf['times']  #new add
    DB_ip = spof_pvc_conf['DB ip']  #new add
    DB_port = int(spof_pvc_conf['DB port']) #new add

    
    file_path = sys.path[0] + '/kraken/kraken' + pvc
    f = open(file_path)
    #if = open(f'./kraken{pvc}') #from spof_pvc_scenario.yaml get pvc value-/kubernetes/res_file/pvctest.yaml
    pvc = yaml.safe_load(f)
    # print('11111111pvc222222',pvc)  #get /kubernetes/res_file/pvctest.yaml info 
    f.close()

    utils._init()
    logger = log.Log()
    utils.set_logger(logger)
    # print('conffff',conf)   #spof_pvc_scenario.yaml
    stor_config = utils.ConfFile(conf)
    print('stor_configgggggg',stor_config)  #<sshv.utils.ConfFile object at 0x101a06ee0>
    actuator = control.IscsiTest(stor_config)
    print('actuatorrrrrrrrr',actuator)       #actuatorrrrrrrrr <sshv.control.IscsiTest object at 0x11098bbb0>

    fault_setter = FaultSetter(spof_pvc_conf, actuator)

    while times:
        STOP_FLAG = None
        PVC_ID = 0
        STOP_CREATE = False
        create_timeout = 1
        # 创建
        print('start creating pvccccccccccccccccccc')
        logging.info("start creating pvc")
        Thread(target=pvc_create,args=(pvc,NAME_SPACE,create_timeout)).start()


        logging.info("start setting failure")
        print('start setting failureeeeeeeeeeeeeeeeeeeeeee')
        # 人工故障设置, kind 设置为 'manual' 时启动
        if fault_setter.manual_setting():
            STOP_FLAG = True
            logging.info("stop the creation of pvc")

        #if fault_setter.shutdown_setting():
         #   STOP_FLAG = True
          #  logging.info("stop the creation of pvc")
           # print('stop the creation of pvcccccccccccccccccc')

        # 故障
        STOP_FLAG = True
        fault_setter.setting()

        # 检查及处理
        logging.info("start checking resource status")
        if not check_pvc_status(NAME_SPACE):
            print('check pvcccccccc statussssssss')
            logging.info("The pvc status is not passed, log collection is performed")
            collect_pvc_describe(NAME_SPACE)
            actuator.get_log(False)
            STOP_CREATE = True
                    
        if not check_drbd_status(NAME_SPACE):
            print('check drbd statussssssss')
            logging.info("The drbd status is not passed, log collection is performed")
            collect_drbd_log(NAME_SPACE)
            actuator.get_log(False)
            STOP_CREATE = True

        # 检查不通过是否停止
        if STOP_CREATE:
            print('resource status is not passed, exit')
            logging.info("resource status is not passed, exit")
            send_email.STMPEmail(mail_receiver,message2='VersaTST test interrupted，Cannot read the kubeconfig file, please check').send_fail()
            database_reliability.Write_database_reliability(DB_ip,DB_port,'spof_pvc',Test_action,'fail',times,Test_times,Test_name)
            return


        # 检查资源是否转移
        if spof_pvc_conf['kind'] == 'interface_down':
            if fault_setter.check_running_node():
                logging.info("resources have been moved to other nodes")
                actuator.get_log(False)

        
        # 清空 pvc
        print('start clearing resourcessssssssssss')
        logging.info("start clearing resources")
        delete_all_pvc(NAME_SPACE)

        # 删除后的检查 
        print('start environment checkkkkkkkkkkkkkkkkkkkk')
        logging.info("start environment check")
        if not is_clean(NAME_SPACE):
            print('The resource is not cleared normallyyyyyyyyyyyyyyy')
            logging.info("The resource is not cleared normally")
            logging.info("collect logs")
            collect_pvc_describe(NAME_SPACE)
            actuator.get_log(False)
            return


        # 恢复环境
        print('recovery environmentttttttttttt')
        logging.info("recovery environment")
        fault_setter.recover()
        time.sleep(10)
        
        # 后置检查及处理
        print("check if the environment is normallllllllllll")
        logging.info("check if the environment is normal")
        if not check_env(pvc,NAME_SPACE):
            print("environment does not pass inspectionnnnnnnnnnnnn")
            logging.info("environment does not pass inspection")
            logging.info("collect logs")
            collect_pvc_describe(NAME_SPACE)
            collect_drbd_log(NAME_SPACE)
            actuator.get_log(False)
            return

        times -= 1
        print("* remaining times:",times)
        if times == 0:
            print('test successssssssssssssssss')
            database_reliability.Write_database_reliability(DB_ip,DB_port,'spof_pvc',Test_action,'pass',Test_times,Test_times,Test_name)
            
        
        
        
def pvc_create(pvc,namesapce,timeout=2):
    time_end = time.time() + timeout
    global PVC_ID
    global STOP_FLAG
    while time.time() <= time_end:
        if STOP_FLAG:
            print('interrupt pvc creationnnnnnnnnnnnnnn')
            logging.info("interrupt pvc creation")
            break
        PVC_ID += 1
        pvc['metadata']['name'] = f'pvc-test{PVC_ID}'
        kubecli.create_pvc_(pvc,namesapce)
    return PVC_ID

def check_pvc_status(namesapce, timeout=5 * 60):
    time.sleep(10)
    time_end = time.time() + timeout
    while time.time() <= time_end:
        bound_num = 0
        pvcs = kubecli.get_all_pvc_status(namespace=namesapce)
        for pvc,state in pvcs.items():
            if state == 'Bound':
                bound_num += 1
            else:
                break

        if len(pvcs) == bound_num:
            return True
        time.sleep(3)   
    print('check pvc status timeoutttttttttttttt')

    logging.info("check pvc status timeout")
    return False

def check_drbd_status(namespace,timeout= 60):
    time_end = time.time() + timeout
    pvs = kubecli.list_pv(namespace=namespace)
    replicas = 3
    success_flag = ['UpToDate','Diskless']

    time.sleep(10)
    print('check linstor status 11111111111')
    while time.time() <= time_end:
        success_pvc = 0
        print('check linstor status starting')
        resources = linstorcli.get_resource()
        print('check linstor statu endinggggggggggg')
        for pv in pvs:
            success_res = 0
            for res in resources:
                if res["Resource"] == pv and res["State"] in success_flag:
                    success_res += 1
            if success_res == replicas:
                success_pvc += 1

        if len(pvs) == success_pvc:
            return True
        
        time.sleep(5)
    print('check drbd status timeouttttttttttt')

    logging.info("check drbd status timeout")
    return False

def delete_all_pvc(namespace):
    kubecli.delete_all_pvc(namespace)
            
def is_clean(namespace, timeout= 3*60):
    time_end = time.time() + timeout
    while time.time() <= time_end:
        flag = True
        pvcs = kubecli.list_pv(namespace=namespace)
        if pvcs:
            flag = False

        drbds = linstorcli.get_resource()
        for pvc in pvcs:
            for drbd in drbds:
                if drbd["Resource"] == pvc:
                    flag = False
                    break

        if flag == True:
            return flag

        time.sleep(3)

    return flag

def check_env(pvc,namespace):
    global PVC_ID
    PVC_ID += 1
    pvc['metadata']['name'] = f'pvc-test-check-env-{PVC_ID}'
    kubecli.create_pvc_(pvc,NAME_SPACE)
    if check_pvc_status(NAME_SPACE) and check_drbd_status(NAME_SPACE):
        kubecli.delete_pvc_(pvc['metadata']['name'],namespace)
        # 检查删除情况
        if is_clean(namespace):
            return True


def collect_pvc_describe(namespace):
    # 收集状态不是Bound的 pvc 的相关信息
    pvcs = kubecli.get_all_pvc_status(namespace=namespace)
    for pvc,state in pvcs.items():
        if state != 'Bound':
            # 收集信息
            # crm_report、kubectl describe PVC和dmesg信息
            describe = get_pvc_describe(pvc,namespace)
            logging.error(describe)

def collect_drbd_log(namespace):
    pvs = kubecli.list_pv(namespace=namespace)
    success_flag = ['UpToDate','Diskless']
    resources = linstorcli.get_resource()
    pvcs = []


    for pv in pvs:
        for res in resources:
            if res["Resource"] == pv and res["State"]  not in success_flag:
                # 收集日志
                pvcs.append(kubecli.get_pvc(pv))
    pvcs = set(pvcs)
    for pvc in pvcs:
        describe = get_pvc_describe(pvc,namespace)
        logging.error(describe)

def get_pvc_describe(pvc,namespace):
    pvc_descibe =  subprocess.getoutput(f'kubectl describe pvc {pvc} -n {namespace}')
    return pvc_descibe

            
class FaultSetter():
    def __init__(self,conf, actuator):
        self.node_running_vip = None
        self.node_running_controller = None
        print('conffffffffffffffffff',conf)
        self.kind = conf['kind']
        self.vip = conf['vip']
        self.linstor_controller = conf['linstor_controller']
        self.actuator = actuator


    def _alarm_handler(self, signum, frame):
        raise TimeoutExpired

    def input_with_timeout(self, prompt, timeout):
        signal.signal(signal.SIGALRM, self._alarm_handler)
        signal.alarm(timeout) # produce SIGALRM in `timeout` seconds
        try:
            return input(prompt)
        except TimeoutExpired:
            pass
        finally:
            signal.alarm(0)

    def get_res_running_node(self,res):
        output = subprocess.getoutput(f'crm res show {res}')
        result =  re.findall(rf"resource {res} is running on: (.*)",output)
        if result:
            return result[0]


    def setting(self):
        if self.kind == 'interface_down':
            print('actuatorrrrrrrrrrrrrrrrrrrrrrrrr',self.actuator)
            self.node_running_vip = self.get_res_running_node(self.vip)
            self.node_running_controller = self.get_res_running_node(self.linstor_controller)
            self.actuator.change_node_interface(False)
        elif self.kind == 'switch_port_down':
            self.actuator.change_switch_port(False)
        elif self.kind == 'node_down':  #new
            self.actuator.down_node()
            print('shutdown nodeeeeeeeeeeeeeeeeee')
            self.shutdown_setting()

    def manual_setting(self,timeout=2):
        if self.kind == 'manual':
            user_input = self.input_with_timeout("Enter y/yes to stop PVC creation: ",timeout)
            if user_input == 'y' or user_input == 'yes':
                return True
            else:
                time.sleep(timeout)
                
    def shutdown_setting(self): #new
        if self.kind == 'node_down':
            print('wait timeeeeeeeeee')
            user_input = input("Enter wait time (second): ")
            user_input = int(user_input)
            time.sleep(user_input)
            return True
            print('wait timeeeeeeeeee enddddddddddddd')

    def recover(self):
        # 故障恢复
        if self.kind == 'switch_port_down':
            self.actuator.change_switch_port(True)
        elif self.kind == 'interface_down':
            self.actuator.change_node_interface(True)


    def check_running_node(self):
        is_transferred = False
        node_vip_now = self.get_res_running_node(self.vip)
        node_controller_now = self.get_res_running_node(self.linstor_controller)

        if node_vip_now != self.node_running_vip:
            print(f'The vip resource has been transferred: {node_vip_now}')
            logging.info(f"The vip resource has been transferred: {node_vip_now} ")
            is_transferred = True

        if node_controller_now != self.node_running_controller:
            print(f"The linstor controller has been transferred: {node_vip_now} ")
            logging.info(f"The linstor controller has been transferred: {node_vip_now} ")
            is_transferred = True

        return is_transferred
        

        

