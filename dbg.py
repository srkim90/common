# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : dbg.py
  Release  : 1
  Date     : 2018-12-16
 
  Description : config module for python
 
  Notes :
  ===================
  History
  ===================
  2018/12/16  created by Kim, Seongrae
'''
import traceback
from log import *
from singleton import *

def do_abort():
    print_call_stack()
    quit()

def print_call_stack(isLog=True, exception=None):
    dbg_line = ["\n"]
    
    e = sys.exc_info()

    call_stack = traceback.format_stack()


    if e[0] == SystemExit:
        return

    dbg_line.append("%s%s%s" % (C_RED, LINE80, C_END))
    if e[2] != None:
        dbg_line.append(" %s%s[ Exception ]%s" % (C_BOLD, C_RED, C_END))
        dbg_line.append("%s%s%s" % (C_RED, line80, C_END))
        dbg_line.append("   %s" % (str(e[0])))
        call_stack = traceback.format_exc().split("\n")
        dbg_line.append("%s%s%s" % (C_RED, line80, C_END))

    dbg_line.append(" %s%s[ Call Stack ]%s" % (C_BOLD, C_YELLOW, C_END))
    dbg_line.append("%s%s%s" % (C_RED, line80, C_END))
    for line in call_stack:
        dbg_line.append("   %s" % line.strip())

    dbg_line.append("%s%s%s\n" % (C_RED, LINE80, C_END))

    for item in dbg_line:
        print("%s" % item)
        if isLog == True:
            LOG(LOG_CRT, "%s" % item)
               
    return

