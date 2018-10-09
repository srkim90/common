# -*- coding: utf-8 -*-

'''
  Author   " Kim, Seongrae
  Filename " gui.py
  Release  " 1
  Date     " 2018-09-03
 
  Description " Stock GUI module
 
  Notes "
  ===================
  History
  ===================
  2018/09/03  created by Kim, Seongrae
'''

import os
import sys
import numpy as np
from time import sleep
from util import *
from singleton import *

is_import = False

PRINT_TYPE_VALUE            = 1
PRINT_TYPE_RATE_END_DAY     = 2
PRINT_TYPE_RATE_YESTER_DAY  = 3


def show_graph(values, time_axis=None, title=None, y_label='value', print_type=False):

    if get_python_runtime() != PYTHON_TYPE_CPYTHON:
        return

    global is_import
    if is_import == False:
        import matplotlib.pyplot as plt 
        is_import = True

    if type(values) != list and type(values) != tuple and type(values) != np.ndarray:
        values = [values,]

    if type(values) != np.ndarray:
        values = np.array(values)
    if type(time_axis) != np.ndarray:
        time_axis = np.array(time_axis)
 
    n_skip = 0
    for idx in range(len(values)):
        if values[idx] <= 0:
            n_skip+=1
        else:
            break
        
    if n_skip != 0:
        values    = values[n_skip:]
        time_axis = time_axis[n_skip:]

    if len(time_axis) != len(values):
        print("Invalid laval: time_axis=%d, values=%d" % (len(time_axis), len(values)))
        return False

    # create two subplots with the shared x and y axes
    ax1 = plt.subplot(1, 2, 1)#sharex=True, sharey=True)
    ax2 = plt.subplot(1, 2, 2)#sharex=True, sharey=True)


    r_values = []

    #axes = plt.gca()
    str_ylabel = ""

    ## Rate
    if print_type == PRINT_TYPE_RATE_END_DAY:
        n_start_value = values[0]
        for idx, val in enumerate(values):
            tmp         = (float(val)/float(n_start_value)) * 100.0
            #print("idx:%d, tmp:%d" % (idx, tmp))
            #values[idx] = tmp
            r_values.append(tmp)
            pass
        ax1.set_ylabel('rate (%)')
        edge = (min(r_values) + max(r_values)) / 20
       # axes.set_ylim([min(r_values) - edge ,105])
        str_ylabel = "rate %"
    #elif print_type == PRINT_TYPE_RATE_YESTER_DAY:
    else:
        n_yday_value = -1
        for idx, val in enumerate(values):
            if n_yday_value == -1:
                #values[idx] = 0
                r_values.append(0)
                n_yday_value = val
                continue
            tmp = 100.0 - (float(val)/float(n_yday_value)) * 100.0
            #print("idx:%d, tmp:%d" % (idx, tmp))
            #values[idx] = tmp
            r_values.append(tmp)
            n_yday_value = val
            pass
        ax1.set_ylabel('rate (%)')
        edge = (min(r_values) + max(r_values)) / 10
        #axes.set_ylim([min(r_values) - edge , max(r_values) + edge])
        str_ylabel = "rate %"

    ## Normal
    edge = (min(values) + max(values)) / 200
    #axes.set_ylim([min(values) - edge ,max(values) + edge])
    str_ylabel = y_label

    ax1.plot(time_axis, values, lw=2)
    ax2.plot(time_axis, r_values, lw=2)
    #ax2.fill_between(time_axis, 0, r_values, facecolor='blue', alpha=0.5)
    ax1.set_ylabel(str_ylabel)

    #for idx in range(len(values)):
    #    print("%s: %s" % (time_axis[idx], values[idx]))

    for ax in ax1, ax2:
        ax.grid(True)

    for label in ax2.get_yticklabels():
        label.set_visible(False)

    #if type(title) == str:
    #    fig.suptitle(title)
    #fig.autofmt_xdate()

    plt.show()

