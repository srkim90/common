# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : dispatch_parse.py
  Release  : 1
  Date     : 2018-07-12
 
  Description : dispatch module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/12  created by Kim, Seongrae
'''
import re
import os
import sys    
import time
import termios
import threading
import fcntl
from abc import *
from time import sleep
#from singleton import *
from log import *

#class dispatch():
#    def run(uri_list, param_list, data):
#        pass

class dispatch_util():
    h2_stat  = {}
    lock     = threading.Semaphore(1)

    def __init__(self, dispatch):
        self.tot_tps    = 0
        self.__dispatch = dispatch
        pass

    def show_api_stat(self, ln_sleep=1.0):
        r_code_dict = []
        tot_tps = 0
        for item in self.h2_stat.keys():
            pos = self.h2_stat[item] 
            oper_str = ""
            for oper in pos.keys():
                if not r_code_dict.count(oper):
                    r_code_dict.append(oper)

        oper_str = "  %-20s   " % ("Result Code")
        for item in r_code_dict:
            oper_str += "%-10s " % (item)

        if oper_str == "":
            PRINT("There is no operation statistic")
            return

        result_list = []
        result_list.append("%s" % (LINE80) )
        result_list.append("%s" % (oper_str))
        result_list.append("%s" % (LINE80))

        for item in self.h2_stat.keys():
            pos = self.h2_stat[item] 
            oper_str = ""
            for idx in r_code_dict:
                if idx not in pos:
                    oper_str += "%-10s " % ("0")
                    continue
                oper_str += "%-10s " % (pos[idx])
                tot_tps  += int(oper_str)
            result_list.append("  %-20s : %s" % (item, oper_str))

        if tot_tps != 0:
            result_list.append("%s" % (line80))
            result_list.append("  TPS : %d" % ((tot_tps - self.tot_tps) * ln_sleep) )

        self.tot_tps = tot_tps
        result_list.append("%s" % (LINE80) )

        x, y = get_xy()
        PRINT("\033[%dd\033[%dG" % (y - len(result_list), 0));

        for i in range(len(result_list)):
            print("%-90s" % (' '))
        
        PRINT("\033[%dd\033[%dG" % (y - len(result_list), 0));

        for item in result_list:
            PRINT("%s" % (item))

    def set_api_stat(self, method, uri, rCode):

        if method == None:
            method = "None"
        if uri == None:
            uri = "/None"

        plist=uri.split('?')

        uri_list    = []
        value_list  = {}

        uri_list    = plist[0].split('/')
        uri_list.remove("")
        uri_count = len(uri_list)
        selectd_item = "Unknown-API"

        for item in self.__dispatch:
            if item[1] != method:
                continue
            __uri_list    = item[2].split('/')
            __uri_list.remove("")

            i         = 0
            for utem2 in __uri_list:
                if i >= uri_count:
                    break
                if utem2 == uri_list[i]:
                    i+=1
                elif  utem2[0] == '{' and utem2[-1] == '}':
                    i+=1
                else:
                    break
            
                #print ("%s:%s %d, %d" % (uri, item[2], uri_count, i))
                if uri_count == i:
                    selectd_item = item[0]
                    break

        self.lock.acquire()
        stat_id = "%s:%s" % (method, selectd_item)
        if stat_id not in self.h2_stat:
            self.h2_stat[stat_id] = {}

        pos = self.h2_stat[stat_id]

        if rCode not in pos:
            pos[rCode] = 0

        pos[rCode] += 1
        self.lock.release()

    def do_request_dispatch(self, req_method, req_path, req_data):

        plist=req_path.split('?')

        uri_list    = []
        value_list  = {}
        pram_list   = {}

        uri_list    = plist[0].split('/')
        uri_list.remove("")
        uri_count = len(uri_list)
        #print("%s" % (req_path))
        if len (plist) > 1:
            tmp_list  = plist[1].split('&')
            for item2 in tmp_list:
                #value_list.append(item2.split('='))
                tmptmp = item2.split('=')
                #print("%s:%s" % (tmptmp[0], tmptmp[1]))
                if len(tmptmp) == 2:
                    value_list[tmptmp[0]] = tmptmp[1]

        #print("%s , %s" % (uri_list, value_list))

        for item in self.__dispatch:
            if item[1] != req_method:
                continue
            __uri_list    = item[2].split('/')
            __uri_list.remove("")
            #print("%s" % (__uri_list ))

            i         = 0
            pram_list = {}
            for utem2 in __uri_list:
                if i >= uri_count:
                    break
                if utem2 == uri_list[i]:
                    i+=1
                elif  utem2[0] == '{' and utem2[-1] == '}':
                    pram_list[utem2[1:-1]] = uri_list[i]
                    i+=1
                else:
                    break
            
            if len(__uri_list) == i and uri_count == i:
                rCode, rData =  item[3].run(pram_list, value_list, req_data)
                #self.set_api_stat(req_method, req_path, rCode)

                return rCode, rData

        return 400, None

