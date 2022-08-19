# coding:utf-8
import paramiko
import re
import time
# from performance_exc import test_databse
# from performance_exc import sql_chart
# from performance_exc import sql_select
# from performance_exc import sql_histogram
# from performance_exc import basic 
# from performance_exc import utils
# from performance_exc import log 
import pymysql
from prettytable.prettytable import from_db_cursor



#dict = {'fio_runtime': '10', 'run_count': '2', 'table_name': 'GZ_performance', 'device_type': 'fs', 'device_fs': '/home/openstcontroller/test_dir', 'bs': '4k;1M', 'rw': 'write', 'IOdepth': '8', 'numjobs': '8', 'test_node_IP': '10.203.1.72', 'test_node_username': 'root', 'test_node_password': 'password', 'DB_IP': '10.203.1.84', 'DB_port': '31730'}



class Get_data_info():
    def __init__(self,table_name):
        self.Text_Table_Name = table_name
 

    def get_data_all(self):
        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test') 
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT * FROM {self.Text_Table_Name}'
        cur.execute(sql_result)
        x = from_db_cursor(cur)
        print (x)
        # print(cur)
        cur.close()
        con.commit()
        con.close()



    def get_iops_data_read(self):

        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,IOPS FROM {self.Text_Table_Name} WHERE Readwrite_type="read"'
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))
        print(dev_fs_value)

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,IOPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}"'
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []
        # print('kkkkkkkkkkkk:',list_key)
        # print('vvvvvvvvvvvvvvvv:',list_value)
        print('listallllllllllllend',list_all)
        cur.close()
        con.commit()
        con.close()



    def get_iops_data_write(self):

        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,IOPS FROM {self.Text_Table_Name} WHERE Readwrite_type="write"'
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))
        print(dev_fs_value)

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,IOPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}" '
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []
        # print('kkkkkkkkkkkk:',list_key)
        # print('vvvvvvvvvvvvvvvv:',list_value)

        cur.close()
        con.commit()
        con.close()

    def get_iops_data_randrw(self):

        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,IOPS FROM {self.Text_Table_Name} WHERE Readwrite_type="randrw" '
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))
        print(dev_fs_value)

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,IOPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}" '
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []

        cur.close()
        con.commit()
        con.close()



    def get_mbps_data_read(self):
        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,MBPS FROM {self.Text_Table_Name} WHERE Readwrite_type="read"'
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,MBPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}" '
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []

        cur.close()
        con.commit()
        con.close()



    def get_mbps_data_write(self):
        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,MBPS FROM {self.Text_Table_Name} WHERE Readwrite_type="write"'
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,MBPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}" '
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []

        cur.close()
        con.commit()
        con.close()

    def get_mbps_data_randrw(self):
        con = pymysql.connect(host='10.203.1.84',port=31730,user='root', passwd='passwd', db='test')
        # con = pymysql.connect(host=self.host,port=self.port,user='root', passwd='passwd', db='test') 
        cur = con.cursor() # create a cursor for connection object
        sql_result = f'SELECT DRBD_type,blocksize,MBPS FROM {self.Text_Table_Name} WHERE Readwrite_type="randrw"'
        cur.execute(sql_result)

        dev_fs_value = []
        for i in cur:
            dev_fs_value.append(i[0])
        dev_fs_value = list(set(dev_fs_value))
        print(dev_fs_value)

        list_all = []
        list_key = []
        list_value = []
        for l in range(len(dev_fs_value)):
            print(l)
            list_key.append("dev_fs")
            list_value.append(dev_fs_value[l])
            sql_result_1 = f'SELECT blocksize,MBPS FROM {self.Text_Table_Name} WHERE DRBD_type="{dev_fs_value[l]}" '
            cur.execute(sql_result_1)
            for ii in cur:
                print(ii)
                list_key.append(ii[0])
                list_value.append(ii[1])
            dict1 = dict(zip(list_key,list_value))
            list_all.append(dict1)
            print(list_all)
            list_key = []
            list_value = []

        cur.close()
        con.commit()
        con.close()







if __name__ == '__main__':
    pass
    #get_data_obj = Get_data_info('randomrw_2205170928_Auto_type')
    # get_data_obj.get_data_all()
    #get_data_obj.get_iops_data()




