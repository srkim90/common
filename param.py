# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : param.py
  Release  : 1
  Date     : 2018-08-29
 
  Description : input parameters handleing module
 
  Notes :
  ===================
  History
  ===================
  2018/08/29  created by Kim, Seongrae
'''

import os
import sys
from time import sleep
from singleton import *

class ParamManager(singleton_instance):
    # --test-val=123
    # -v 123
    # --test-val 123
    C_END     = "\033[0m"
    C_BOLD    = "\033[1m"
    C_UNDERLN = "\033[4m"
    param_help = []
    overview_help = ""
    def __init__(self):
        param_dict = {}
        s_key   = None
        for i in range(len(sys.argv)):
            val = sys.argv[i]
            if val[0] == '-':
                if s_key != None:
                    param_dict[s_key] = True
                s_key = None
                if val.find('=') != -1 and val[1] == '-':
                    s_val = val.split('=')
                    key = s_val[0]
                    param_val = ""
                    for item in s_val[1:]:
                        param_val += "=%s" % item
                    param_val = param_val[1:]
                    #print ("s_key:%s, val:%s" % (key, param_val))
                    param_dict[key] = param_val
                else:
                    s_key = val

            elif s_key != None:
                #print ("s_key:%s, val:%s" % (s_key, val))
                param_dict[s_key] = val
                s_key = None

        self.n_params   = len(param_dict)
        self.param_dict = param_dict

    def check_param(self, key):
        if type(key) != list and type(key) != tuple:
            key = (key)

        for item_key in key:
            if item_key in self.param_dict.keys():
                return True
        return False

    def set_param_help(self, key, description ):
        self.param_help.append((key, description))

    def set_overview_help(self, description ):
        if self.overview_help != "":
            if self.overview_help[-1] != '\n':
                self.overview_help += '\n'

        self.overview_help += description

    def print_help_string(self, print_fn=None):
        str_help    = ""
        str_tab     = "    "
        str_help   += "%sOVERVIEW%s" % (self.C_BOLD, self.C_END)
        sp_overview = self.overview_help.split('\n')

        for item in sp_overview:
            str_help += "\n%s%s%s" % (str_tab, str_tab, item)

        str_help += "\n%sOPTIONS%s" % (self.C_BOLD, self.C_END)

        for item in self.param_help:
            key = item[0]
            description = item[1]
            
            if type(key) != list and type(key) != tuple:
                key = (key)
 
            str_key = ""
            for a_key in key:
                str_key += ",%s" % (a_key)
        
            str_key = str_key[1:]

            str_help += "\n%s%s%s%s%s\n%s%s%s%s" % (str_tab, str_tab, self.C_BOLD, self.C_UNDERLN, str_key, str_tab, str_tab, str_tab, description)
        if print_fn != None:
            print_fn(str_help)
        else:
            print(str_help)
        return str_help

    def get_param_values(self, key, default_value=None):
        if type(key) == str:
            key = [key]
        elif type(key) == list or type(key) == tuple:
            pass
        else:
            return None

        for k_item in key:
            if k_item in self.param_dict.keys():
                return self.param_dict[k_item]

        return default_value

def init_param():
    ParamManager.instance()

def get_param(key, default_value=None):
    e = ParamManager.getinstance()
    return e.get_param_values(key, default_value)
    


