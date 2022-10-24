# -*- coding: utf-8 -*-
import os
import sys
import yaml
from kraken.kraken.kubernetes import client as kubecli
from kraken.kraken.spof_pvc_scenarios import setup as spof_pvc_scenarios
from kraken.linstorclient import client as linstorcli
from kraken.sshv import send_email


def test_spoc_pvc(cfg):

    with open(cfg, "r") as f:
        config = yaml.full_load(f)
    with open(sys.path[0] + '/kraken/scenarios/spof_pvc_scenario.yaml', 'r', encoding='utf-8') as sps:
        data = yaml.full_load(sps)
        mail_receiver = data.get('mail_receive')
    distribution = config["kraken"].get("distribution")
    global kubeconfig_path, wait_duration
    if 'kubernetes' in str(distribution):
        kubeconfig_path = config["kraken"].get("kubeconfig_path", "")
        chaos_scenarios = config["kraken"].get("chaos_scenarios", [])
        if chaos_scenarios:
            for scenario in chaos_scenarios:
                scenario_type = list(scenario.keys())[0]
                scenarios_list = scenario[scenario_type]
                if not os.path.isfile(kubeconfig_path):
                    print('', "Cannot read the kubeconfig file at %s, please check" % kubeconfig_path,0)
                    send_email.STMPEmail(mail_receiver,message2='VersaTST test interrupted，Cannot read the kubeconfig file, please check').send_fail()
                    #logging.error("Cannot read the kubeconfig file at %s, please check" % kubeconfig_path)
                    sys.exit(1)
                    print('', "Initializing client to talk to the Kubernetes cluster",0)
            #logging.info("Initializing client to talk to the Kubernetes cluster")
                os.environ["KUBECONFIG"] = str(kubeconfig_path)
                kubecli.initialize_clients(kubeconfig_path)
                print(scenarios_list)

                if scenario_type == "spof_pvc_scenarios":
                    print("Running spof pvc scenario")
                    linstorcli.initialize_clients()
                    spof_pvc_scenarios.run(scenarios_list,config)





class Handle_pvc_yaml():
    def __init__(self,data,pvc_path):
        self.data = data
        self.pvc_path = pvc_path
        self.handle_pvctestYaml()


    def handle_pvctestYaml(self): 
        storage_classname = self.data['storageclass_name']
        pvc_size = self.data['pvc_size']
        file_path = sys.path[0] + self.pvc_path # '/kraken/kraken/kubernetes/res_file/pvctest.yaml'
        with open(file_path) as f:
            doc = yaml.full_load(f)
        # print('docccccccccc',doc)
        doc['spec']['resources']['requests']['storage'] = pvc_size
        doc['spec']['storageClassName'] = storage_classname
        with open(file_path, 'w') as f:
            yaml.dump(doc,f,sort_keys=False) 



class Handle_spof_yaml():
    def __init__(self,data,spof_path):
        self.data = data
        print('sssssssssdataaaaaaaaaa',self.data)
        self.spof_path = spof_path
        self.handle_spofYaml()

    def handle_spofYaml(self): 
        DB_ip = self.data['DB_IP']
        DB_port = self.data['DB_port']
        Test_name = self.data['test_name']
        mail_receiver = ','.join(self.data['mail_receiver'])
        try:
            vip = self.data['crm_vip_name']
            linstor_controller = self.data['crm_controller_name']
        except:
            pass
        kind = self.data['test_action']
        print('kindddddddddd',kind)
        runs = self.data['test_times']
        file_path = sys.path[0] + self.spof_path #'/kraken/scenarios/spof_pvc_scenario.yaml'
        with open(file_path) as f:
            doc = yaml.full_load(f)
        try: 
            doc['vip'] = vip
            doc['linstor_controller'] = linstor_controller
        except:
            pass

        doc['DB ip'] = DB_ip
        doc['DB port'] = DB_port
        doc['name'] = Test_name
        doc['kind'] = kind
        doc['times'] = int(runs)
        doc['mail_receiver'] = mail_receiver
    
        if kind == 'switch_port_down':
            print('test down switch')
            down_switch_info = self.data['down_switch']
            switch_info = self.handle_downtypeInfo(down_switch_info)
            doc['spof_scenario']['down_switch']['ip']=switch_info['ip']
            doc['spof_scenario']['down_switch']['port']=switch_info['port']

        if kind == 'interface_down':
            print('test down interface')
            down_interface_info = self.data['down_interface']
            interface_info = self.handle_downtypeInfo(down_interface_info)
            doc['spof_scenario']['down_interface_host']['hostname']=interface_info['hostname']
            doc['spof_scenario']['down_interface_host']['public_ip']= interface_info['public_ip']
            doc['spof_scenario']['down_interface_host']['password']= interface_info['password']
            doc['spof_scenario']['down_interface_host']['interface']= interface_info['interface']
        
        if kind == 'node_down':  
            print('test down host')
            down_host_info = self.data['down_host']
            host_info = self.handle_downtypeInfo(down_host_info)
            doc['spof_scenario']['down_host']['hostname']=host_info['hostname']
            doc['spof_scenario']['down_host']['public_ip']=host_info['public_ip']
            doc['spof_scenario']['down_host']['password']=host_info['password']

        if kind == 'manual':  
            print('test manual')

        storage_node_info = self.data['storage_node']
        storage_info = self.handle_vplxInfo(storage_node_info)
        doc['versaplx'] = storage_info


        with open(file_path, 'w') as f:
            yaml.dump(doc,f,sort_keys=False)  
        with open(file_path, 'r') as fpr:
            content = fpr.read()
            if "'" in content:
                content = content.replace("'", ' ')
            with open(file_path, 'w') as fpw:
                 fpw.write(content)


    def handle_downtypeInfo(self,data): 
        if ',' in data:
            data = data.split(',')
        elif ';' in data:
            data = data.split(';')
        else:
            data = data.split()
        info_key = []
        info_value = []
        for i in range(len(data)):
            aa=data[i].split(':')
            info_key.append(aa[0])
            info_value.append(aa[1])
        dict1 = dict(zip(info_key,info_value))
        return dict1


    def handle_vplxInfo(self,data): 
        info_key = []
        info_value = []
        dict_versaplx = []
        if '&&' in data:
            data = data.split('&&')
        for i in range(len(data)):
            if ',' in data[i]:
                data_deal = data[i].split(',')
            elif ';' in data[i]:
                data_deal = data[i].split(';')
            else:
                data_deal = data[i].split()
            for i in range(len(data_deal)):
                data_dealll = data_deal[i].split(':')
                info_key.append(data_dealll[0])
                info_value.append(data_dealll[1])
            dict1 = dict(zip(info_key,info_value))
            dict_versaplx.append(dict1)
        return dict_versaplx




if __name__ == "__main__":
    pass




