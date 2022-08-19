# coding:utf-8
import paramiko
import re
import time
from performance_exc import test_databse
from performance_exc import sql_chart
from performance_exc import sql_select
from performance_exc import sql_histogram
from performance_exc import basic 
from performance_exc import utils
from performance_exc import log 
#import test_databse
#import sql_chart
#import sql_select
#import sql_histogram
#import basic 
import pymysql
import sys
#import utils
#import log
# import sshv.utils as utils
# import sshv.log as log



#dict = {'fio_runtime': '10', 'run_count': '2', 'table_name': 'GZ_performance', 'device_type': 'fs', 'device_fs': '/home/openstcontroller/test_dir', 'bs': '4k;1M', 'rw': 'write', 'IOdepth': '8', 'numjobs': '8', 'test_node_IP': '10.203.1.72', 'test_node_username': 'root', 'test_node_password': 'password', 'DB_IP': '10.203.1.84', 'DB_port': '31730'}



class Get_config_info():
    def __init__(self,data):
        self.data = data
        # self.get_ssh()
        # self.get_device_type()
 

    def get_ssh(self): 
        IP = self.data['test_node_IP']
        username = self.data['test_node_username']
        passwd = self.data['test_node_password']
        utils.prt_log('', f"Get ssh info", 0)
        # print("get ssh info")
        return IP,username,passwd

    def get_run_count(self): 
        count = self.data['run_count']
        if count == "":
            count = 1
        else:
            count = int(count)
        utils.prt_log('', f"Get run_count info,default=1", 0)
        #print("Get run_count info,default=1")
        return count

    def get_device_type(self): 
        d_type = self.data['device_type']
        utils.prt_log('', f"Get device_type info", 0)
        # print("get device_type info")
        return d_type

    def get_device_info(self): 
        block_fs = self.data['device_fs']
        if ',' in block_fs:
            block_fs = block_fs.split(',')
        elif ';' in block_fs:
            block_fs = block_fs.split(';')
        else:
            block_fs = block_fs.split()
        utils.prt_log('', f"Get block device or filesystem test info,needs to be separated by the , or ; symbol", 0)
        # print("get block device or fs test info")
        return block_fs

    def get_bs_info(self): 
        bs_all = ['1k','2k','4k','8k','16k','32k','64k','128k','256k','512k','1M','2M']
        bs = self.data['bs']
        # print('bsssbbbssssssss',bs)
        if '-' in bs:
            bs = bs.split('-')
            for i in range(len(bs)):
                #print('bbbbss',bs[i])
                begin = bs_all.index(bs[0])
            end = bs_all.index(bs[i])
            fix_end = end + 1
            bs = bs_all[begin:fix_end]

        elif ',' in bs:
            bs = bs.split(',')
        elif ';' in bs:
            bs = bs.split(';')
        else:
            bs = bs.split()
        utils.prt_log('', f"Get block size info,needs to be separated by the , or ; symbol", 0)
        # print("get bs info")
        return bs

    def get_rw_info(self): 
        rw = self.data['rw']
        if ',' in rw:
            rw = rw.split(',')
        elif ';' in rw:
            rw = rw.split(';')
        else:
            rw = rw.split()
            #print("The test rw type or fs needs to be separated by the , or ; symbol")
        utils.prt_log('', f"Get read write type info,needs to be separated by the , or ; symbol", 0)
        return rw

    def get_iodepth_info(self): 
        iodepth = self.data['IOdepth']
        if ',' in iodepth:
            iodepth = iodepth.split(',')
        elif ';' in iodepth:
            iodepth = iodepth.split(';')
        else:
            iodepth = iodepth.split()
            #print('lennnnn',len(iodepth))
            #print(type(iodepth))
            #print("The test iodepth or fs needs to be separated by the , or ; symbol")
        utils.prt_log('', f"Get iodepth info,needs to be separated by the , or ; symbol", 0)
        return iodepth

    def get_numjobs_info(self): 
        numjobs = self.data['numjobs']
        if ',' in numjobs:
            numjobs = numjobs.split(',')
        elif ';' in numjobs:
            numjobs = numjobs.split(';')
        else:
            numjobs = numjobs.split()
            #print("The test numjobs or fs needs to be separated by the , or ; symbol")
        utils.prt_log('', f"Get numjobs info,needs to be separated by the , or ; symbol", 0)
        # print("get numjobs info")
        return numjobs

    def get_runtime_info(self): 
        run_time = self.data['fio_runtime']
        if run_time == "":
            run_time = "180"
        utils.prt_log('', f"Get run_time info,default=180s", 0)
        # print("get run_time info")  
        return run_time

    def get_tbname_info(self): 
        t_name = self.data['table_name']
        # time_n = time.localtime(time.time())
        # Date = time.strftime('%Y%m%d_%H%M',time_n) 
        if t_name != "":
            t_name = t_name
        else:
            t_name = 'GZ_performance'
        utils.prt_log('', f"Get table_name info,default=GZ_performance_date", 0)
        # print("get table_name info")
        return t_name

    def get_DB_info(self): 
        DB_IP = self.data['DB_IP']
        DB_port = self.data['DB_port']
        utils.prt_log('', f"Get DB_IP DB_port info", 0)
        # print("get device_type info from database")
        return DB_IP,DB_port



class Self_defined_scenarios(object):
    def __init__(self,frontend_data):
        utils.prt_log('', f"RUN Self_defined_scenarios test...", 0)
        self.frontend_data = frontend_data
        # basic_fun = basic.Basic_function()
        # print_info = basic_fun.sql_print_index()
        #if Index_Table not existed,return error

        obj_conf = Get_config_info(self.frontend_data)
        self.ssh_IP,self.ssh_username,self.ssh_passwd = obj_conf.get_ssh()
        self.d_type = obj_conf.get_device_type()
        self.runtime = obj_conf.get_runtime_info()
        self.block_fs = obj_conf.get_device_info()
        self.bs = obj_conf.get_bs_info()
        self.rw = obj_conf.get_rw_info()
        self.iodepth = obj_conf.get_iodepth_info()
        self.numjobs = obj_conf.get_numjobs_info()
        self.get_fio_command()
        self.clname = obj_conf.get_tbname_info()
        time_n = time.localtime(time.time())
        self.Date = time.strftime('%y%m%d%H%M',time_n)
        self.Disk_Type = "Auto_type"
        self.Text_Table_Name = (self.clname + '_' + self.Date + '_' + self.Disk_Type)


        self.execute_fio_command()

        self.DB_IP,DB_port = obj_conf.get_DB_info()
        self.DB_port = int(DB_port)
        # utils.prt_log('', f"Print Index table and table information from database...........  ", 0)
        self.write_to_database()
        self.write_config()
        utils.prt_log('', f"Write test result to database", 0)
        self.get_db_info()
        self.write_to_excel()
        self.draw_chart()
        self.draw_histogram()
        utils.prt_log('', f"RUN Self_defined_scenarios test... Done ", 0)



    def write_config(self): 
        file_path = sys.path[0] + '/performance_exc/selfdefined_config.txt'
        with open(file_path,'w') as f:
            f.write("table_name:"+self.Text_Table_Name+"\n"+"DB_IP:"+str(self.DB_IP)+"\n"+"DB_port:"+str(self.DB_port))


    def get_fio_command(self): 
        obj_con = Handle_config_info(self.d_type,self.runtime,self.block_fs,self.rw,self.bs,self.iodepth,self.numjobs)
        self.command_list = obj_con.handle_config_info()


    def execute_fio_command(self): 
        if self.d_type == "block":
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list)
            test_result_list =  obj_run.run_fio_command()
        else:
            obj_clear = Get_clear_command(self.block_fs)
            clear_command_list = obj_clear.clear_copy()
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list,clear_command_list)
            self.test_result_list = obj_run.run_fio_command()


    def write_to_database(self): 
        test_databse.Write_to_database(self.DB_IP,self.DB_port,self.Text_Table_Name,self.clname,self.Date,self.Disk_Type,self.test_result_list)


    def get_db_info(self): 
        get_info = sql_chart.Get_info_db(self.DB_IP,self.DB_port,self.Text_Table_Name)
        self.rwType_info = get_info.get_rwType_db()
        self.bs_info = get_info.get_bs_db()
        self.nj_info = get_info.get_nj_db()
        self.iod_info = get_info.get_IOdepth_db()
        self.dev_info = get_info.get_device_db()
        #excel = sql_select.sql_write_excel(self.Text_Table_Name,self.rw)


    def write_to_excel(self): 
        excel = sql_select.sql_write_excel(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info)
        excel.write_to_excel_all()   
        utils.prt_log('', f"Write all data to excel one table automatically , Done", 0)     
        # print('write to excel all, Done!')
        if self.d_type == "filesystem":
            self.per_setting = {'directory': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        else:
            self.per_setting = {'filename': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        for i in range(len(self.rwType_info)):
            excel.get_data_IO_MB(self.rwType_info[i])
            #self.per_setting = {'directory': ['/home/openstcontroller/test_dir'], 'bs': ['1k', '2k'], 'rw': ['write'], 'iodepth': ['8'], 'numjobs': ['8']}
            excel.write_to_excel_bs(self.per_setting,self.rwType_info[i],self.iod_info,self.nj_info)
        utils.prt_log('', f"Write all data to excel bs table automatically , Done", 0) 

    def draw_chart(self): 
        # call get DB_info function,do not use self.bs
        sql_chart.sql_graph_chart(self.DB_IP,self.DB_port,self.Text_Table_Name,self.bs_info,self.rwType_info,self.iod_info,self.nj_info)
        utils.prt_log('', f"Draw line chart picture, Done", 0) 
        # print('Draw chart picture , Done!')
        
    def draw_histogram(self): 
        IOPS_4K_list = ['IOPS','4k']
        MBPS_1M_list = ['MBPS','1M']
        histogram_run = sql_histogram.sql_graph_histogram(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info,self.iod_info,self.nj_info)

        fn_l,val=histogram_run.get_data_histogram(IOPS_4K_list)
        if len(val) != 0:
            histogram_run.draw_graph_histogram(fn_l,val)
            # print('Draw IOPS_4K histogram picture , Done!')
            utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
            # print('Not draw histogram picture,because data is null')
        fn_l2,val2=histogram_run.get_data_histogram(MBPS_1M_list)
        if len(val2) != 0:
            histogram_run.draw_graph_histogram(fn_l2,val2)
            # print('Draw MBPS_1M histogram picture , Done!')
            utils.prt_log('', f"Draw MBPS_1M histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
            # print('Not draw histogram picture,because data is null')
    


class Seq_rw_scenarios(object):
    def __init__(self,frontend_data):
        utils.prt_log('', f"RUN Seq_rw_scenarios test...", 0)
        self.frontend_data = frontend_data
        obj_conf = Get_config_info(self.frontend_data)
        self.ssh_IP,self.ssh_username,self.ssh_passwd = obj_conf.get_ssh()

        self.d_type = obj_conf.get_device_type()
        self.runtime = obj_conf.get_runtime_info()
        self.block_fs = obj_conf.get_device_info()
        self.bs = ['1k','2k','4k','8k', '16k', '32k', '64k', '128k', '256k', '512k', '1M','2M']
        #self.bs = ['4k', '1M'] #, '4k', '8k', '16k', '32k', '64k', '128k', '256k', '512k', '1M','2M'
        self.rw = ['read', 'write']
        self.iodepth = ['8']
        self.numjobs = ['8']
        self.get_fio_command()

        self.tbname = obj_conf.get_tbname_info()
        self.DB_info = obj_conf.get_DB_info()
        self.execute_fio_command()
        # utils.prt_log('', f"Get config file information ", 0)
        self.DB_IP,DB_port = obj_conf.get_DB_info()
        self.DB_port = int(DB_port)

        self.clname = obj_conf.get_tbname_info()
        time_n = time.localtime(time.time())
        self.Date = time.strftime('%y%m%d%H%M',time_n)
        self.Disk_Type = "Auto_type"
        self.Text_Table_Name = (self.clname + '_' + self.Date + '_' + self.Disk_Type)

        # utils.prt_log('', f"Print Index table and table information from database...........  ", 0)
        self.write_to_database()
        self.write_config()
        utils.prt_log('', f"Write test result to database", 0)
        self.get_db_info()
        self.write_to_excel()
        self.draw_chart()
        self.draw_histogram()
        utils.prt_log('', f"RUN Seq_rw_scenarios test... Done ", 0)

    def write_config(self): 
        file_path = sys.path[0] + '/performance_exc/seqrw_config.txt'
        with open(file_path,'w') as f:
            f.write("table_name:"+self.Text_Table_Name+"\n"+"DB_IP:"+str(self.DB_IP)+"\n"+"DB_port:"+str(self.DB_port))

    def get_fio_command(self): 
        obj_con = Handle_config_info(self.d_type,self.runtime,self.block_fs,self.rw,self.bs,self.iodepth,self.numjobs)
        self.command_list = obj_con.handle_config_info()


    def execute_fio_command(self): 
        if self.d_type == "block":
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list)
            test_result_list =  obj_run.run_fio_command()
        else:
            obj_clear = Get_clear_command(self.block_fs)
            clear_command_list = obj_clear.clear_copy()
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list,clear_command_list)
            self.test_result_list = obj_run.run_fio_command()
            # print('test_result_listtttttttttttttttttt',self.test_result_list)

    def write_to_database(self): 
        test_databse.Write_to_database(self.DB_IP,self.DB_port,self.Text_Table_Name,self.clname,self.Date,self.Disk_Type,self.test_result_list)


    def get_db_info(self): 
        get_info = sql_chart.Get_info_db(self.DB_IP,self.DB_port,self.Text_Table_Name)
        self.rwType_info = get_info.get_rwType_db()
        self.bs_info = get_info.get_bs_db()
        self.nj_info = get_info.get_nj_db()
        self.iod_info = get_info.get_IOdepth_db()
        self.dev_info = get_info.get_device_db()
        #excel = sql_select.sql_write_excel(self.Text_Table_Name,self.rw)


    def write_to_excel(self): 
        excel = sql_select.sql_write_excel(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info)
        excel.write_to_excel_all()  
        utils.prt_log('', f"Write all data to excel one table automatically , Done", 0)       
        if self.d_type == "filesystem":
            self.per_setting = {'directory': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        else:
            self.per_setting = {'filename': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        for i in range(len(self.rwType_info)):
            excel.get_data_IO_MB(self.rwType_info[i])
            #self.per_setting = {'directory': ['/home/openstcontroller/test_dir'], 'bs': ['1k', '2k'], 'rw': ['write'], 'iodepth': ['8'], 'numjobs': ['8']}
            excel.write_to_excel_bs(self.per_setting,self.rwType_info[i],self.iod_info,self.nj_info)
        utils.prt_log('', f"Write all data to excel bs table automatically , Done", 0) 
            # print('write to excel bs, Done!')

    def draw_chart(self): 
        # call get DB_info function,do not use self.bs
        sql_chart.sql_graph_chart(self.DB_IP,self.DB_port,self.Text_Table_Name,self.bs_info,self.rwType_info,self.iod_info,self.nj_info)
        utils.prt_log('', f"Draw line chart picture, Done", 0) 
        # print('Draw chart picture , Done!')
        
    def draw_histogram(self): 
        IOPS_4K_list = ['IOPS','4k']
        MBPS_1M_list = ['MBPS','1M']
        histogram_run = sql_histogram.sql_graph_histogram(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info,self.iod_info,self.nj_info)

        fn_l,val=histogram_run.get_data_histogram(IOPS_4K_list)
        if len(val) != 0:
            histogram_run.draw_graph_histogram(fn_l,val)
            # print('Draw IOPS_4K histogram picture , Done!')
            utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
        fn_l2,val2=histogram_run.get_data_histogram(MBPS_1M_list)
        if len(val2) != 0:
            histogram_run.draw_graph_histogram(fn_l2,val2)
            # print('Draw MBPS_1M histogram picture , Done!')
            utils.prt_log('', f"Draw MBPS_1M histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
    




class Video_scenarios(object):
    def __init__(self,frontend_data):
        utils.prt_log('', f"RUN Video_scenarios test...", 0)
        self.frontend_data = frontend_data
        obj_conf = Get_config_info(self.frontend_data)
        self.ssh_IP,self.ssh_username,self.ssh_passwd = obj_conf.get_ssh()

        self.d_type = obj_conf.get_device_type()
        self.runtime = obj_conf.get_runtime_info()
        self.block_fs = obj_conf.get_device_info()
        self.bs = ['64k','128k','256k','512k','1M'] #, '256k', '512k', '1M'
        #self.bs = ['4k', '1M'] #, '256k', '512k', '1M'
        self.rw = ['read', 'write']
        self.iodepth = ['8']
        self.numjobs = ['1']
        self.get_fio_command()

        self.tbname = obj_conf.get_tbname_info()
        self.DB_info = obj_conf.get_DB_info()
        self.execute_fio_command()

        self.DB_IP,DB_port = obj_conf.get_DB_info()
        self.DB_port = int(DB_port)
        self.clname = obj_conf.get_tbname_info()
        time_n = time.localtime(time.time())
        self.Date = time.strftime('%y%m%d%H%M',time_n)
        self.Disk_Type = "Auto_type"
        self.Text_Table_Name = (self.clname + '_' + self.Date + '_' + self.Disk_Type)

        # utils.prt_log('', f"Print Index table and table information from database...........  ", 0)
        self.write_to_database()
        self.write_config()
        utils.prt_log('', f"Write test result to database", 0)
        self.get_db_info()
        self.write_to_excel()
        self.draw_chart()
        self.draw_histogram()
        utils.prt_log('', f"RUN Video_scenarios test... Done ", 0)
        # utils.prt_log('', f"Get config file information ", 0)

    def write_config(self): 
        file_path = sys.path[0] + '/performance_exc/video_config.txt'
        with open(file_path,'w') as f:
            f.write("table_name:"+self.Text_Table_Name+"\n"+"DB_IP:"+str(self.DB_IP)+"\n"+"DB_port:"+str(self.DB_port))

    def get_fio_command(self): 
        obj_con = Handle_config_info(self.d_type,self.runtime,self.block_fs,self.rw,self.bs,self.iodepth,self.numjobs)
        self.command_list = obj_con.handle_config_info()


    def execute_fio_command(self): 
        if self.d_type == "block":
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list)
            test_result_list =  obj_run.run_fio_command()
        else:
            obj_clear = Get_clear_command(self.block_fs)
            clear_command_list = obj_clear.clear_copy()
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list,clear_command_list)
            self.test_result_list = obj_run.run_fio_command()

    def write_to_database(self): 
        test_databse.Write_to_database(self.DB_IP,self.DB_port,self.Text_Table_Name,self.clname,self.Date,self.Disk_Type,self.test_result_list)


    def get_db_info(self): 
        get_info = sql_chart.Get_info_db(self.DB_IP,self.DB_port,self.Text_Table_Name)
        self.rwType_info = get_info.get_rwType_db()
        self.bs_info = get_info.get_bs_db()
        self.nj_info = get_info.get_nj_db()
        self.iod_info = get_info.get_IOdepth_db()
        self.dev_info = get_info.get_device_db()
        #excel = sql_select.sql_write_excel(self.Text_Table_Name,self.rw)


    def write_to_excel(self): 
        excel = sql_select.sql_write_excel(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info)
        excel.write_to_excel_all()    
        utils.prt_log('', f"Write all data to excel one table automatically , Done", 0)      
        # print('write to excel all, Done!')
        if self.d_type == "filesystem":
            self.per_setting = {'directory': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        else:
            self.per_setting = {'filename': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        for i in range(len(self.rwType_info)):
            excel.get_data_IO_MB(self.rwType_info[i])
            #self.per_setting = {'directory': ['/home/openstcontroller/test_dir'], 'bs': ['1k', '2k'], 'rw': ['write'], 'iodepth': ['8'], 'numjobs': ['8']}
            excel.write_to_excel_bs(self.per_setting,self.rwType_info[i],self.iod_info,self.nj_info)
            # print('write to excel bs, Done!')
        utils.prt_log('', f"Write all data to excel bs table automatically , Done", 0) 

    def draw_chart(self): 
        # call get DB_info function,do not use self.bs
        sql_chart.sql_graph_chart(self.DB_IP,self.DB_port,self.Text_Table_Name,self.bs_info,self.rwType_info,self.iod_info,self.nj_info)
        utils.prt_log('', f"Draw line chart picture, Done", 0) 
        # print('Draw chart picture , Done!')
        
    def draw_histogram(self): 
        IOPS_4K_list = ['IOPS','4k']
        MBPS_1M_list = ['MBPS','1M']
        histogram_run = sql_histogram.sql_graph_histogram(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info,self.iod_info,self.nj_info)

        fn_l,val=histogram_run.get_data_histogram(IOPS_4K_list)
        if len(val) != 0:
            histogram_run.draw_graph_histogram(fn_l,val)
            utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
            # print('Draw IOPS_4K histogram picture , Done!')
            # utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
            # print('Not draw histogram picture,because data is null')
        fn_l2,val2=histogram_run.get_data_histogram(MBPS_1M_list)
        if len(val2) != 0:
            histogram_run.draw_graph_histogram(fn_l2,val2)
            # print('Draw MBPS_1M histogram picture , Done!')
            utils.prt_log('', f"Draw MBPS_1M histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
    





class Random_rw_scenarios(object):  
    def __init__(self,frontend_data):
        utils.prt_log('', f"RUN Random_rw_scenarios test...", 0)
        self.frontend_data = frontend_data
        obj_conf = Get_config_info(self.frontend_data)
        self.ssh_IP,self.ssh_username,self.ssh_passwd = obj_conf.get_ssh()

        self.d_type = obj_conf.get_device_type()
        self.runtime = obj_conf.get_runtime_info()
        self.block_fs = obj_conf.get_device_info()
        self.bs = ['1k','2k','4k']#, '8k', '16k', '32k', '64k'
        #self.bs = ['1k','2k','4k','8k','16k','32k','64k']#, '8k', '16k', '32k', '64k'
        self.rw = ['randrw']
        self.iodepth = ['8']
        self.numjobs = ['16']
        self.get_fio_command()
        # utils.prt_log('', f"Get config file information ", 0)

        self.tbname = obj_conf.get_tbname_info()
        self.DB_info = obj_conf.get_DB_info()
        self.execute_fio_command()

        self.DB_IP,DB_port = obj_conf.get_DB_info()
        self.DB_port = int(DB_port)
        self.clname = obj_conf.get_tbname_info()
        time_n = time.localtime(time.time())
        self.Date = time.strftime('%y%m%d%H%M',time_n)
        self.Disk_Type = "Auto_type"
        self.Text_Table_Name = (self.clname + '_' + self.Date + '_' + self.Disk_Type)

        # utils.prt_log('', f"Print Index table and table information from database...........  ", 0)
        self.write_to_database()
        self.write_config()
        utils.prt_log('', f"Write test result to database", 0)
        self.get_db_info()
        self.write_to_excel()
        self.draw_chart()
        self.draw_histogram()
        utils.prt_log('', f"RUN Random_rw_scenarios test... Done ", 0)

    def write_config(self): 
        file_path = sys.path[0] + '/performance_exc/randomrw_config.txt'
        with open(file_path,'w') as f:
            f.write("table_name:"+self.Text_Table_Name+"\n"+"DB_IP:"+str(self.DB_IP)+"\n"+"DB_port:"+str(self.DB_port))

    def get_fio_command(self): 
        obj_con = Handle_config_info(self.d_type,self.runtime,self.block_fs,self.rw,self.bs,self.iodepth,self.numjobs)
        self.command_list = obj_con.handle_config_info()

    def execute_fio_command(self): 
        if self.d_type == "block":
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list)
            self.test_result_list =  obj_run.run_fio_command()
        else:
            obj_clear = Get_clear_command(self.block_fs)
            clear_command_list = obj_clear.clear_copy()
            obj_run = Run_fio(self.ssh_IP,self.ssh_username,self.ssh_passwd,self.command_list,clear_command_list)
            self.test_result_list = obj_run.run_fio_command()

    def write_to_database(self): 
        test_databse.Write_to_database(self.DB_IP,self.DB_port,self.Text_Table_Name,self.clname,self.Date,self.Disk_Type,self.test_result_list)


    def get_db_info(self): 
        get_info = sql_chart.Get_info_db(self.DB_IP,self.DB_port,self.Text_Table_Name)
        self.rwType_info = get_info.get_rwType_db()
        self.bs_info = get_info.get_bs_db()
        self.nj_info = get_info.get_nj_db()
        self.iod_info = get_info.get_IOdepth_db()
        self.dev_info = get_info.get_device_db()
        #excel = sql_select.sql_write_excel(self.Text_Table_Name,self.rw)


    def write_to_excel(self): 
        excel = sql_select.sql_write_excel(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info)
        excel.write_to_excel_all()        
        utils.prt_log('', f"Write all data to excel one table automatically , Done", 0)
        # print('write to excel all, Done!')
        if self.d_type == "filesystem":
            self.per_setting = {'directory': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        else:
            self.per_setting = {'filename': self.dev_info,'bs' : self.bs_info,'rw' : self.rwType_info,'iodepth' : self.iod_info,'numjobs': self.nj_info}
        for i in range(len(self.rwType_info)):
            excel.get_data_IO_MB(self.rwType_info[i])
            #self.per_setting = {'directory': ['/home/openstcontroller/test_dir'], 'bs': ['1k', '2k'], 'rw': ['write'], 'iodepth': ['8'], 'numjobs': ['8']}
            excel.write_to_excel_bs(self.per_setting,self.rwType_info[i],self.iod_info,self.nj_info)
        utils.prt_log('', f"Write all data to excel bs table automatically , Done", 0)

    def draw_chart(self): 
        # call get DB_info function,do not use self.bs
        sql_chart.sql_graph_chart(self.DB_IP,self.DB_port,self.Text_Table_Name,self.bs_info,self.rwType_info,self.iod_info,self.nj_info)
        utils.prt_log('', f"Draw line chart picture, Done", 0) 
        
    def draw_histogram(self): 
        IOPS_4K_list = ['IOPS','4k']
        MBPS_1M_list = ['MBPS','1M']
        histogram_run = sql_histogram.sql_graph_histogram(self.DB_IP,self.DB_port,self.Text_Table_Name,self.rwType_info,self.iod_info,self.nj_info)

        fn_l,val=histogram_run.get_data_histogram(IOPS_4K_list)
        if len(val) != 0:
            histogram_run.draw_graph_histogram(fn_l,val)
            utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
            # utils.prt_log('', f"Draw IOPS_4k histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
        fn_l2,val2=histogram_run.get_data_histogram(MBPS_1M_list)
        if len(val2) != 0:
            histogram_run.draw_graph_histogram(fn_l2,val2)
            utils.prt_log('', f"Draw MBPS_1M histogram picture , Done", 0)
        else:
            utils.prt_log('', f"Not draw histogram picture,because data is null", 0)
    





class Handle_config_info(object):
    def __init__(self,test_type,runtime,block_fs,rw,bs,iodepth,numjobs):
        self.test_type = test_type
        self.runtime = runtime
        self.block_fs = block_fs
        self.rw = rw
        self.bs = bs
        self.iodepth = iodepth
        self.numjobs = numjobs
        # self.handle_config_info()
        # self.clear_copy()

    def handle_config_info(self):
    #how to handle filename test or direcory test
        command_list = []
        #test_info_type = "directory"
        if self.test_type == "block":
            for dev in range(len(self.block_fs)):
                for rw_type in range(len(self.rw)):
                    for b_s in range(len(self.bs)):
                        # print(b_s)
                        for iod in range(len(self.iodepth)):
                            for njs in range(len(self.numjobs)):
                                test_name=self.block_fs[dev].split('/')[-1]+'_'+self.rw[rw_type]+'_'+self.bs[b_s]+'_'+self.iodepth[iod]+'_'+self.numjobs[njs]
                                # print(test_name)
                                # print('rwtypeeeeeeeeee1111111111',self.rw[rw_type])
                                if self.rw[rw_type] == "randrw":
                                    fio_command = "fio" + " --name=" + test_name + " --ioengine=libaio --direct=1 --ramp_time=10 --rwmixread=75 --group_reporting --new_group"+ " --runtime=" +self.runtime + " --filename=" +self.block_fs[dev] + " --rw=" + self.rw[rw_type] + " --bs="+self.bs[b_s] + " --iodepth=" + self.iodepth[iod]+ " --numjobs="+self.numjobs[njs]
                                    command_list.append(fio_command)
                                    # print('3333333333',command_list)
                                else:
                                    fio_command = "fio" + " --name=" + test_name + " --ioengine=libaio --direct=1 --ramp_time=10 --group_reporting --new_group"+ " --runtime=" +self.runtime + " --filename=" +self.block_fs[dev] + " --rw=" + self.rw[rw_type] + " --bs="+self.bs[b_s] + " --iodepth=" + self.iodepth[iod]+ " --numjobs="+self.numjobs[njs]
                                    # print(fio_command)
                                    command_list.append(fio_command)
        else:
            for dev in range(len(self.block_fs)):
                # print(dev)
                for rw_type in range(len(self.rw)):
                    for b_s in range(len(self.bs)):
                        # print(b_s)
                        for iod in range(len(self.iodepth)):
                            for njs in range(len(self.numjobs)):
                                test_name=self.block_fs[dev].split('/')[-1]+'_'+self.rw[rw_type]+'_'+self.bs[b_s]+'_'+self.iodepth[iod]+'_'+self.numjobs[njs]
                                # print(test_name)
                                # print('rwtypeeeeeeeeee2222',self.rw[rw_type])
                                if self.rw[rw_type] == "randrw":
                                    fio_command = "fio" + " --name=" + test_name + " --ioengine=libaio --direct=1 --ramp_time=10 --rwmixread=75 --group_reporting --new_group --size=10G"+ " --runtime=" +self.runtime + " --directory=" +self.block_fs[dev] + " --rw=" + self.rw[rw_type] + " --bs="+self.bs[b_s] + " --iodepth=" + self.iodepth[iod]+ " --numjobs="+self.numjobs[njs]
                                    command_list.append(fio_command) 
                                else:
                                    fio_command = "fio" + " --name=" + test_name + " --ioengine=libaio --direct=1 --ramp_time=10 --group_reporting --new_group --size=10G"+ " --runtime=" +self.runtime + " --directory=" +self.block_fs[dev] + " --rw=" + self.rw[rw_type] + " --bs="+self.bs[b_s] + " --iodepth=" + self.iodepth[iod]+ " --numjobs="+self.numjobs[njs]
                                # print(fio_command)
                                    command_list.append(fio_command)       

        # print('999999999999',command_list)
        utils.prt_log('', f"Create fio command automatically", 0)
        return command_list


class Get_clear_command(object):
    def __init__(self,block_fs):
        self.block_fs = block_fs

    def clear_copy(self):
        clear_command_list = []
        for dev in range(len(self.block_fs)):
            command='rm -f ' + self.block_fs[dev] + '/*'
            clear_command_list.append(command)
        # print(clear_command_list)
        utils.prt_log('', f"Create fio clear command automatically,for loop test", 0)
        return clear_command_list            




class Run_fio(object):
    def __init__(self,hostname,username,password,command_list,clear_command_list=[]):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.command_list = command_list
        self.clear_command_list = clear_command_list

        #self.hci=Handle_config_info()
        #self.command_list=self.hci.handle_config_info()
        # self.clear_command_list=self.hci.clear_copy()
        # print(self.command_list)
        # self.run_fio_command()
        # self.run_clear_command()

    def run_fio_command(self):
        self.list_data = []
        try:
            self.ssh = paramiko.SSHClient()
            know_host = paramiko.AutoAddPolicy()
            self.ssh.set_missing_host_key_policy(know_host)
            self.ssh.connect(
                hostname = self.hostname,
                port = 22,
                username = self.username,
                password = self.password
            )
            utils.prt_log('', f"SSH to test node success!", 0)
            # print('sshssssssssssssssssssssssuccess')
            for i in range(len(self.command_list)):
                if '--directory' in self.command_list[0]:
                    #self.clear_command_list=self.hci.clear_copy()  
                    self.run_clear_command()
                stdin,stdout,stderr = self.ssh.exec_command(self.command_list[i])
                # print('sssssscccccclisttttttt',self.command_list[i])
                utils.prt_log('', f"RUN fio command:   {self.command_list[i]}", 0)
                fio_result=stdout.read().decode()
                # print('fiorrrrrrrrrrrrssss',fio_result)
                if fio_result == "":
                    utils.prt_log('', f"Test node not install fio,please check!", 2)
                    # print('Test node not install fio,please check!')
                    #print('tyepppppeeeeeeeeeeeeeeeeeeeeeee',type(fio_result))
                elif "No such file or directory" in fio_result:
                    utils.prt_log('', f"Test device or filesystem does not exist,please check!", 2)
                    # print('Test device or filesystem does not exist,please check!')
                    #no fio fio_result is kong;no device or fs,fio_result is error=No such file or directory
                else:
                    handle_data=Handle_data_function(fio_result)
                    result_data=handle_data.handle_mbps()
                    self.list_data.append(result_data)
            # print(self.list_data)
            utils.prt_log('', f"Handle IOPS MBPS result", 0)
            self.ssh.close()
            utils.prt_log('', f"Close ssh connection...", 0)
            return self.list_data

        except:
            utils.prt_log('', f"Failed to connect test node,Please check!", 2)
            # print("Failed to connect test node,Please check!!!")



    def run_clear_command(self):
        # ssh = paramiko.SSHClient()
        # know_host = paramiko.AutoAddPolicy()
        # ssh.set_missing_host_key_policy(know_host)
        # ssh.connect(
        #     hostname = self.hostname,
        #     port = 22,
        #     username = self.username,
        #     password = self.password
        # )
        for i in range(len(self.clear_command_list)):
            try:
                stdin,stdout,stderr = self.ssh.exec_command(self.clear_command_list[i])
                result=stdout.read().decode()
                utils.prt_log('', f"Clear the data in the file system, loop test", 0)
                # print('Clear the data in the file system, loop test')
            except:
                utils.prt_log('', f"Failed to execute clear command {self.clear_command_list[i]}", 1)
                # print(f"Failed to execute clear command {self.clear_command_list[i]}")
            # print(result)
        # ssh.close()





class Handle_data_function(object):
    def __init__(self,result):
        # self.file_input = file_input
        self.result = result
        self.list_data = []
        self.get_all_data()
        self.handle_iops()


    def get_all_data(self):
        # file = open(self.file_input,'r')
        # results = file.read()
        re_=r'([a-zA-Z0-9_]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_(\d+)_(\d+).*\s*.*IOPS=([a-zA-Z0-9.]+).*\s*.*B/s\s\((.+/s)\)' # Regular Expression
        re_pattern = re.compile(re_)
        re_result = re_pattern.findall(self.result)
        # print('rrrrrrrrrrsssssss',re_result)

        for i in re_result:
            self.list_data.append(list(i))
        # print('sssssssssss',self.list_data)
        # file.close()


    def handle_iops(self):
        for data in self.list_data:
            iops_value = data[5]
            if iops_value == '':
                data[5]= ''
            elif iops_value[-1]=='k': 
                IOPS_k = float(float(iops_value[:-1]) * 1000)
                data[5] = IOPS_k
            else:
                IOPS_r = float(iops_value)
        # utils.prt_log('', f"Handle IOPS result", 0)

    def handle_mbps(self):
        for data in self.list_data:
            mbps_value = data[6]
            if mbps_value == '':
                data[6]= ''
            elif mbps_value[3:][-4:] == 'kB/s': 
                MBPS_k = float(mbps_value[:-4]) / 1000
                MBPS_k = float("%.2f" % MBPS_k)
                data[6]= MBPS_k
            elif mbps_value[3:][-4:] == 'GB/s':
                MBPS_g = float((mbps_value[:-4]))*1.07
                MBPS_g = float("%.1f" % MBPS_g)
                MBPS_g = int(MBPS_g*1000)
                data[6]= MBPS_g
            else:
                MBPS_r = float(mbps_value[:-4]) 
                data[6]= MBPS_r
        # print('oooooooooooo',self.list_data[0])
        # utils.prt_log('', f"Handle MBPS result", 0)

        return self.list_data[0]





if __name__ == '__main__':
    pass
    #utils._init()
    #logger = log.Log()
    #utils.set_logger(logger)
    # test=Handle_config_info()
    #Self_defined_scenarios(dict)
    # Seq_rw_scenarios(dict)
    # Video_scenarios(dict)
    # Random_rw_scenarios(dict)
    #test=Run_fio()



