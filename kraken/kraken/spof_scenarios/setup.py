import sys
import yaml
import re
import json
import threading
import queue
import time
import re
from os import path
from kraken.kraken.cerberus import setup as cerberus
from kraken.kraken.kubernetes import client as kubecli
from kraken.kraken.invoke import command as runcommand
from kraken.kraken.pvc import pvc_scenario as pvc_scenario
from kraken.sshv import utils as utils
from kraken.sshv import log as log
from kraken.sshv import control as control
from kraken.sshv import k8s_connect as k8s_connect
from kraken.sshv import send_email

#import kraken.cerberus.setup as cerberus
#import kraken.kubernetes.client as kubecli
#import kraken.invoke.command as runcommand
#import kraken.pvc.pvc_scenario as pvc_scenario
#import sshv.utils as utils
#import sshv.log as log
#import sshv.control as control
#import sshv.k8s_connect as k8s_connect



def update_yaml(pvc,state):
        with open(pvc) as f:
            doc = yaml.safe_load(f)
        doc['spec']['storageClassName'] = state[0]
        doc['spec']['resources']['requests']['storage'] = state[1]
        with open(pvc, 'w') as f:
            yaml.safe_dump(doc, f, default_flow_style=False)



def run(scenarios_list, config):

	namespace = "default"
	failed_post_scenarios = ""
	go_meter_pod = ""
	lins_blkpvc_file = scenarios_list[0][0]
	gomet_pod_file = scenarios_list[1][0]
	stor_file = scenarios_list[2][0]
	write_q = queue.Queue(maxsize = 1)
	update_yaml(lins_blkpvc_file,config)

	stor_config = utils.ConfFile(stor_file)
	kind = config[2]
	times = int(config[3])
	pvc_size = config[1]

	k8s_connect.k8s_init("kraken/config/config_spof.yaml")

	versa_con = control.IscsiTest(stor_config)

	crm_location_node = versa_con.get_glinstor_location_node()
	pvc_resoure = kubecli.create_pvc(lins_blkpvc_file)
	time.sleep(20)
	with open(sys.path[0] + '/kraken/scenarios/spof_scenario.yaml', 'r', encoding='utf-8') as sps:
		data = yaml.full_load(sps)
		mail_receiver = data.get('mail_receive')
	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.safe_load(f)
		metadata_config = gomet_pod_config["metadata"]
		go_meter_pod = metadata_config.get("name", "")
		kubecli.create_pod_spof(gomet_pod_config, namespace,lins_blkpvc_file, 120)

	time.sleep(2)


	err = versa_con.check_drbd_crm_res(pvc_resoure, False)
	if not err:	
		err = versa_con.ckeck_drbd_status(pvc_resoure)
	err = 1
	while(err == 1):
		err = versa_con.ckeck_drbd_status(pvc_resoure)
		time.sleep(2)
	if err:
		nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
		return times,nowtime	

	# err = versa_con.ckeck_drbd_status_spof(pvc_resoure, False)
	# if err:
	# 	clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
	# 	exit(1)
	left_times = times
	while(left_times):
		down = False
		utils.prt_log('', "Times %d: For single failure, Go-meter start to write" % (times - left_times),0)
		start_time = time.time()	
		threading.Thread(target=gometer_write, args=(go_meter_pod, write_q, pvc_size)).start()
		time.sleep(10)
		if kind == "node_down":
			versa_con.down_node_ipmi()
			down = True
		elif kind == "interface_down":
			versa_con.change_node_interface(False)
		elif kind == "switch_port_down":
			versa_con.change_switch_port(False)
		elif kind == "hand_operation":
			utils.prt_log('', "Please do manual operation...",0)
		utils.prt_log('', "Go-meter is writing, wait...",0)
		time.sleep(10)

		result_down = check_if_change(versa_con,kind,0)

		err = write_q.get()
		end_time = time.time()
		write_time = int(end_time-start_time)
		utils.prt_log('', "Go-meter finish writing, write time: %ds" % write_time,0)
		if not result_down or write_time<25:
			if kind == "interface_down":
				versa_con.change_node_interface(True)
			elif kind == "switch_port_down":
				versa_con.change_switch_port(True)
				send_email.STMPEmail(mail_receiver,
									 message2='VersaTST test interrupted，Single fault have not been done before go-meter finish writing…').send_fail()
			utils.prt_log('', "Single fault have not been done before go-meter finish writing...",0)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime

		if err:
			if kind == "interface_down":
				versa_con.change_node_interface(True)
			elif kind == "switch_port_down":
				versa_con.change_switch_port(True)
			send_email.STMPEmail(mail_receiver,
								 message2='VersaTST test interrupted，Go meter write failed').send_fail()
			utils.prt_log('', "Go meter write failed",0)
			versa_con.get_log(down)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime			

		err_drbd = versa_con.ckeck_drbd_status_spof(pvc_resoure, down)
		err_crm = versa_con.check_drbd_crm_res(pvc_resoure, down)
		if err_drbd or err_crm:
			if kind == "interface_down":
				versa_con.change_node_interface(True)
			elif kind == "switch_port_down":
				versa_con.change_switch_port(True)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)		
			return left_times,nowtime

		# err = versa_con.ckeck_drbd_status_spof(pvc_resoure, down)
		# if err:
		# 	clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
		# 	exit(1)

		utils.prt_log('', "Go-meter start to compare",0)
		command = "cd /go/src/app;./main compare"
		response = kubecli.exec_cmd_in_pod_sh(command, go_meter_pod, namespace)
		utils.prt_log('', "\n" + str(response),0)

		if not "Finish" in response:
			send_email.STMPEmail(mail_receiver,
								 message2='VersaTST test interrupted，Go meter write failed').send_fail()
			utils.prt_log('', "Go meter compare failed",0)
			if kind == "interface_down":
				versa_con.change_node_interface(True)
			elif kind == "switch_port_down":
				versa_con.change_switch_port(True)
			versa_con.get_log(down)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime

		utils.prt_log('', "Times %d:For fix single failure, Go-meter start to write" % (times - left_times),0)
		start_time = time.time()
		threading.Thread(target=gometer_write, args=(go_meter_pod, write_q, pvc_size)).start()
		if kind == "interface_down":
			versa_con.change_node_interface(True)
		elif kind == "node_down":
			versa_con.power_node_ipmi()
			#versa_con.check_if_on()
		elif kind == "switch_port_down":
			versa_con.change_switch_port(True)
		elif kind == "hand_operation":
			utils.prt_log('', "Please do manual operation to fix...",0)


		down = False
		utils.prt_log('', "Go-meter is writing, wait...",0)
		time.sleep(20)
		result_down = check_if_change(versa_con,kind,1)
		err = write_q.get()
		end_time = time.time()
		write_time = int(end_time-start_time)
		utils.prt_log('', "Go-meter finish writing, write time: %ds" % write_time,0)
		versa_con.check_if_on(kind)
		if not result_down or write_time<25:
			send_email.STMPEmail(mail_receiver,
								 message2='VersaTST test interrupted，Single fault have not been fixed before go-meter finish writing').send_fail()
			utils.prt_log('', "Single fault have not been fixed before go-meter finish writing...",0)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime

		if err:
			utils.prt_log('', "Go meter write failed",0)
			versa_con.get_log(down)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime		

		err_drbd = versa_con.ckeck_drbd_status_spof(pvc_resoure, down)
		err_crm = versa_con.check_drbd_crm_res(pvc_resoure, down)
		if err_drbd or err_crm:
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)		
			return left_times,nowtime
		# err = versa_con.ckeck_drbd_status_spof(pvc_resoure, down)
		# if err:
		# 	clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
		# 	exit(1)
		utils.prt_log('', "Go-meter start to compare",0)
		command = "cd /go/src/app;./main compare"
		response = kubecli.exec_cmd_in_pod_sh(command, go_meter_pod, namespace)
		utils.prt_log('', "\n" + str(response),0)

		if not "Finish" in response:
			utils.prt_log('', "Go meter compare failed",0)
			versa_con.get_log(down)
			nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
			return left_times,nowtime
		if(left_times == times):
			versa_con.get_log(down)

		if kind == "node_down":
			err = versa_con.move_back_crm_res(crm_location_node)
			if err:
				utils.prt_log('', "Moved back crm res failed...",0)
				send_email.STMPEmail(mail_receiver,
									 message2='VersaTST test interrupted，Moved back crm res failed…').send_fail()
				versa_con.get_log(down)
				nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
				return left_times,nowtime

		left_times = left_times - 1
		time.sleep(10)
	nowtime = clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file)
	return 0,nowtime


def run11(scenarios_list, config):
	namespace = "default"
	failed_post_scenarios = ""
	#for app_config in scenarios_list:

	lins_blkpvc_file = scenarios_list[0][0]
	stor_file = scenarios_list[2][0]
	gomet_pod_file = scenarios_list[1][0]
	update_yaml(lins_blkpvc_file,config)
	stor_config = utils.ConfFile(stor_file)
	write_q = queue.Queue(maxsize = 1)
	kind = config[2]
	times = int(config[3])
	pvc_size = config[1]

	#k8s_connect.k8s_init("kraken/config/config_spof.yaml")

	versa_con = control.IscsiTest(stor_config)
	#pvc_resoure = kubecli.create_pvc(lins_blkpvc_file)
	#print(pvc_resoure)
	#time.sleep(20)
	
	with open(path.join(path.dirname(__file__), gomet_pod_file)) as f:
		gomet_pod_config = yaml.safe_load(f)
		metadata_config = gomet_pod_config["metadata"]
		go_meter_pod = metadata_config.get("name", "")
		#kubecli.create_pod_spof(gomet_pod_config, namespace,lins_blkpvc_file, 120)

	time.sleep(2)
	#check_if_change(versa_con,kind,1)
	versa_con.down_node_ipmi()
	time.sleep(20)
	#versa_con.power_node_ipmi()
	# threading.Thread(target=gometer_write, args=(go_meter_pod, write_q, pvc_size)).start()
	# err = write_q.get()
	# print(err)
	# err = write_q.get()
	exit()


def clear_pvc_and_pod(go_meter_pod,namespace,lins_blkpvc_file):
	nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	kubecli.delete_pod(go_meter_pod, namespace)
	kubecli.delete_pvc(lins_blkpvc_file)
	return nowtime

def check_if_change(versa_con,kind,if_on):
	if kind == "interface_down":
		err = versa_con.check_node_interface(if_on)
		if not err:
			return 1
		else:
			utils.prt_log(None, "Interface is not changed!!! ",0)
			return 0
	# elif kind == "switch_port_down":
	# 	err = versa_con.check_switch_port(if_on)
	# 	if not err:
	# 		return 1
	# 	else:
	# 		prt_log(None, "Port is not changed!!! ",0)
	# 		return 0
	return 1




def gometer_write(pod_name, write_q,pvc_size):
	print(pvc_size)
	if "1G" in pvc_size:
		pvc_size = "1000M"
	halfCount = int(re.sub("\D", "", pvc_size))
	halfCount = int(halfCount/2)
	unit = ''.join(re.findall(r'[A-Za-z]', pvc_size))
	pvc_size = str(halfCount) + unit
	print(pvc_size)
	#command = 'cd /go/src/app;echo {Lineage: [0,2], JobNum: 2, BlockSize: 16K, TotalSize: 20M, MasterMask: 12312311, DevicePath: /dev/sde} > go-meter.yaml' % pvc_size
	#command = "cd /go/src/app;./main write"
	#response = kubecli.exec_cmd_in_pod_sh(command, pod_name, "default")
	#utils.prt_log('', "\n" + str(response),0)
	command = "cd /go/src/app;./main write -t %s" % pvc_size
	response = kubecli.exec_cmd_in_pod_sh(command, pod_name, "default")
	utils.prt_log('', "\n" + str(response),0)

	if "Finish" in response:
		if not "重试" in response:
			write_q.put(0)
		else:
			write_q.put(1)
	else:
		write_q.put(1)


