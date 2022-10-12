# -*- coding: utf-8 -*-
import os
import sys
import yaml
import time
from prettytable.prettytable import from_db_cursor
import pymysql
from kraken.sshv import send_email




class Write_database_reliability(object):
    def __init__(self,host,port,Test_scenario,Test_action,Test_result,Test_times,Expected_times,Test_name):
        self.host = host
        self.port = port
        self.Test_scenario = Test_scenario
        self.Test_action = Test_action
        self.Test_result = Test_result
        self.Test_times = Test_times
        self.Expected_times = Expected_times
        self.Test_name = Test_name
        time_n = time.localtime(time.time())
        self.Date = time.strftime('%y%m%d%H%M',time_n)
        self.create_index_tb()

 
    def create_index_tb(self):
        with open(sys.path[0] + '/kraken/scenarios/spof_pvc_scenario.yaml', 'r', encoding='utf-8') as sps:
            data = yaml.full_load(sps)
            mail_receiver = data.get['mail_receive']
        con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') # create connection object and database file
        cur = con.cursor()

        try:
            cur.execute('''CREATE TABLE Index_Table_reliability
                            (Test_scenario text,
                            Test_action text,
                            Test_result text,
                            Test_times text,
                            Expected_times text,
                            Test_date text,
                            Test_name text
                            )''')
        except:
            print('Table already exist!')
            pass
        
        check_query = 'SELECT Test_name from Index_Table_reliability'
        cur.execute (check_query)
        check_table_name = []
        for row in cur:
             check_table_name.append(row[0])
        if self.Test_name in check_table_name:
            print ("The table already exist! Please check")
            send_email.STMPEmail(mail_receiver,
                                 message2='VersaTST test interrupted，The table already exist! Please check').send_fail()
            sys.exit()

        query = '''INSERT INTO Index_Table_reliability (Test_scenario, Test_action, Test_result, Test_times, Expected_times, Test_date, Test_name) values (%s, %s, %s, %s, %s, %s, %s)'''
        values = (self.Test_scenario, self.Test_action,self.Test_result, self.Test_times, self.Expected_times, self.Date, self.Test_name) 
        cur.execute (query,values)
        
        sql_sentence = cur.execute('SELECT * FROM Index_Table_reliability')
        x = from_db_cursor(cur)
        print (x)
        cur.close()
        con.commit()
        con.close()


class Get_dbinfo_reliability(object):
    def __init__(self,file_path):
        self.file_path = file_path

    def get_info(self): 
        if os.path.exists(self.file_path) == True:
            with open(self.file_path, "r") as f:
                spof_pvc_conf = yaml.full_load(f)
                db_ip = spof_pvc_conf['DB ip']
                db_port = int(spof_pvc_conf['DB port'])
                table_name = spof_pvc_conf['name']
        con = pymysql.connect(host=db_ip,port=db_port,user='root', passwd='passwd', db='test')
        cur = con.cursor() 
        sql_result = f'SELECT * FROM Index_Table_reliability WHERE Test_name="{table_name}"'
        cur.execute(sql_result)
        list_key = ['Test_scenario','Test_action','Test_result','Test_times','Expected_times','Test_date','Test_name']
        list_value = []
        for i in cur:
            for ii in i:
                list_value.append(ii)
        dict1 = dict(zip(list_key,list_value))
        dict_list = []
        dict_list.append(dict1)
        dict_data = {"code": 0, "msg": "", "count": 1, "data": dict_list}
        return dict_data



if __name__ == "__main__":
    pass



 
