# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : ftp_client.py
  Release  : 1
  Date     : 2018-08-30
 
  Description : ftp client module
 
  Notes :
  ===================
  History
  ===================
  2018/08/30  created by Kim, Seongrae
'''

from ftplib import FTP
import os
import sys
import threading
from time import sleep

from log import *
from singleton import *
from multiprocessing.pool import Pool

TH_BASE_SEND_UNIT = 32

class FtpClient(singleton_instance):
    local_lock = None
    send_queue = []
    def __init__(self, server_ipaddr, user_name, pw, server_port=22, n_work_th=4):
        self.server_ipaddr = server_ipaddr
        print ("server_port: %s, type:%s" % (server_port, type(server_port)))
        self.server_port   = server_port if type(server_port) == int else int(server_port)
        self.n_work_th     = n_work_th
        self.user_name     = user_name
        self.pw            = pw
        self.local_lock    = threading.Semaphore(1)

        for i in range(n_work_th):
            hThread = threading.Thread(target=self._ftp_th)
            hThread.daemon = True
            hThread.start()

    def push_ftp(self, server_dir, file_list):
        if type(file_list) == str:
            file_list = [file_list,]
        elif type(file_list) != list and type(file_list) != tuple:
            PRINT("Error: Invalid input data type=%s" % (type(file_list)))
            return False

        self.local_lock.acquire()
        for item in file_list:
            pair = (server_dir, item)
            self.send_queue.append(pair)
        self.local_lock.release()
        return True

    def _ftp_th(self):
        while True:
            self.local_lock.acquire()
            now_q_size  = len(self.send_queue)

            if now_q_size == 0:
                self.local_lock.release()
                sleep(0.01)
                continue

            copy_len    = TH_BASE_SEND_UNIT if now_q_size >= TH_BASE_SEND_UNIT else now_q_size
            local_queue = self.send_queue[0:copy_len]
            if copy_len < now_q_size:
                self.send_queue = self.send_queue[copy_len:]
            else:
                self.send_queue = []
            self.local_lock.release()

        
            dict_send_pair = {}
            for pair in local_queue:
                server_dir, file_name = pair

                if server_dir in dict_send_pair.keys():
                    dict_send_pair[server_dir].append(file_name)
                else:
                    dict_send_pair[server_dir] = [file_name,]

            for server_dir in dict_send_pair.keys(): 
                self._send_proc(server_dir, dict_send_pair[server_dir])

 
    def _send_proc(self, server_dir, file_list):
        ftp = FTP()
        ftp.connect(self.server_ipaddr, port=self.server_port)
        ftp.login(user=self.user_name, passwd=self.pw)
        #ftp = FTP(self.server_ipaddr, user=self.user_name, passwd=self.pw)
        #ftp.login()

        #print("server_dir: %s, file_list: %s, server_ipaddr: %s, server_port: %s, user_name: %s, pw: %s" % (server_dir, file_list, self.server_ipaddr, self.server_port, self.user_name, self.pw))

        n_list  = ftp.nlst(server_dir + "/..")
        new_dir = server_dir.split('/')[-1]
        print ("n_list:%s, new_dir:%s" % (n_list, new_dir))

        f_mkdir = 1
        for item in n_list:
            item = item.split('/')[-1]
            if item == new_dir:
                f_mkdir = 0
                break

        if f_mkdir == 1:
           ftp.mkd(server_dir)
        ftp.cwd(server_dir)

        for item in file_list:
            ftp.storbinary("STOR %s" % (item.split('\\')[-1]), open(item,'rb') )

        ftp.quit()



def init_ftp(server_ipaddr, user_name, pw, port=22,  n_work_th=4):
    FtpClient.instance(server_ipaddr, user_name, pw, server_port=port, n_work_th=n_work_th)

def push_ftp(server_dir, file_list):
    e = FtpClient.getinstance()
    e.push_ftp(server_dir, file_list)

