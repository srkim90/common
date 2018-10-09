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
from util import *
#import numpy as np
from time import sleep
from singleton import *
import abc
from collections import Iterable
from log import *
import datetime
import copy
CHART_TYPE_AREA=1


def js_dict_to_string(dict_obj, level=0):
    str_tab  = ' '*4
    str_dict = "{"
    prefix   = ""
    for key in dict_obj.keys():
        #if isinstance(dict_obj[key], Iterable) == True:
        if type(dict_obj[key]) == dict:
            str_dict += "%s%s: %s" % (prefix, key, js_dict_to_string(dict_obj[key], level + 1))
        else:
            if type(dict_obj[key]) == str:
                value = "'%s'" % dict_obj[key]
            else:
                 value = "%s" % dict_obj[key]
            str_dict += "%s%s: %s" % (prefix, key, value)
        if level == 0:
            prefix = ",\n%s%s%s" % (str_tab, str_tab, str_tab)
        else:
            prefix = ", "

    if level == 0:
        str_dict += "\n%s%s}" % (str_tab, str_tab)
    else:
        str_dict += "}"

    return str_dict

class ChartBuilder():
    __metaclass__ = abc.ABCMeta
    def build_chart(self, recodes, time_axis, idx, title_axis=None, title="No name"):

        if title_axis == None:
            if isinstance(recodes[0], Iterable) == False:
                recodes    = [recodes,]
                title_axis = ["Data1" ]
            else:
                title_axis = ["Data%d" % (i + 1) for i in range(len(recodes))]

        if len(recodes[0]) != len(time_axis):
            if len(recodes[0]) < len(time_axis):
                time_axis = time_axis[0:len(recodes[0])]
            else:
                PRINT("Error. Invalid length of data : recodes=%d, time_axis=%d" % (len(recodes[0]), len(time_axis)))
                return None, None

        axis_group    = self._find_data_v_axis_group(recodes)
        function_name = "drawChart_%03d" % (idx)
        chart_data    = self._build_chart_data(recodes, time_axis, title_axis)
        chart_options = self._build_chart_options(title, axis_group=axis_group, h_min=min(recodes[0]), h_max=max(recodes[0]))
        chart_object  = self._build_chart_object(function_name)
        str_js  = "function %s()\n" % (function_name)
        str_js += "     {\n"
        str_js += "        var data     = google.visualization.arrayToDataTable(%s%s);\n" % (chart_data, " "*4)
        str_js += "        var options  = %s;\n" % (chart_options)
        str_js += "        var chart    = %s;\n" % (chart_object)
        str_js += "        chart.draw(data, options);\n"
        str_js += "     }\n"

        return function_name, str_js

    def _find_data_v_axis_group(self, recodes):
        avg_list = []
        group    = []
        for axis in recodes:
            avg_list.append(sum(axis)/len(axis))
    
        if min(avg_list) * 2 < max(avg_list):
            group = [[], []]
            median_value = (min(avg_list) + max(avg_list)) / 2
            for idx, item in enumerate(avg_list):
                if item > median_value:
                    group[0].append(idx)
                else:
                    group[1].append(idx)
        else:
            group = [i for i in range(len(recodes))]
            group = [group,]

        return group

    @abc.abstractmethod
    def _build_chart_data(self, recodes, time_axis, title_axis):
        pass
    @abc.abstractmethod
    def _build_chart_options(self, title, h_min=-1, h_max=-1):
        pass
    @abc.abstractmethod
    def _build_chart_object(self):
        pass


class ChartBuilderArea(ChartBuilder):
    def _build_chart_data(self, recodes, time_axis, title_axis):
        chart_data = []
        str_tab    = ' ' * 4

        recode     = ["Time"]
        for idx, label in enumerate(title_axis):
            recode.append(label)
        chart_data.append(recode)

        for idx, time in enumerate(time_axis):
            recode     = [time, ]
            f_continue = 0
            for data in recodes:
                if data[idx] == -1:
                    f_continue = 1
                    break
                recode.append(data[idx])
            if f_continue == 1:
                continue
            chart_data.append(recode)

        str_chart_data  = "[\n"
        for idx, recode in enumerate(chart_data):
            str_chart_data += "%s%s" % (str_tab * 2, recode)
            if idx + 1 != len(chart_data):
                str_chart_data += ",\n"
            else:
                str_chart_data += "\n"
        str_chart_data += "%s]\n" % (str_tab)
        return str_chart_data

    def _build_chart_options(self, title, axis_group=None, h_min=-1, h_max=-1):
        chart_option = {}
        #print("title: <%s>" % title)
        viewWindow = {}
        if h_min != -1:
            viewWindow["min"] = h_min
        if h_max != -1:
            viewWindow["max"] = h_max
        #if viewWindow != {}:
        #    vAxis["viewWindow"] = viewWindow
        Axis = {"minValue": 0}

        chart_option['title'] =  title
        #chart_option['vAxis'] =  vAxis
        chart_option['hAxis'] = {"title": 'Year',  "titleTextStyle": {"color": '#333'}}
        #series : { 2: {targetAxisIndex:1}, 0: {targetAxisIndex:0},1: {targetAxisIndex:0}}
        if axis_group != None:
            dict_series = {}
            for idx, sub_group in enumerate(axis_group):
                for idx2, item in enumerate(sub_group):
                    dict_series[item] = { "targetAxisIndex": idx }
            chart_option['series'] = dict_series

        return "%s" % js_dict_to_string(chart_option)

    def _build_chart_object(self, char_obj_name):
        str_js  = "new google.visualization.AreaChart(document.getElementById('%s'))" % (char_obj_name)
        return str_js


class GoogleChart(singleton_instance):
    def __init__(self, html_path, browser_name='firefox -new-tab '):
        self.idx          = 0
        self.browser_name = browser_name
        self.html_path    = html_path
        self.function_name     = []
        self.str_js            = []
        if not os.path.isdir(html_path):
            os.mkdir(html_path)

    def add_chart(self, recodes, time_axis, chart_type=CHART_TYPE_AREA, title_axis=None, title="No name"):
        if chart_type == CHART_TYPE_AREA:
            bulder = ChartBuilderArea()
        else:
            return False
        self.idx += 1

        recodes   = copy.deepcopy(recodes)
        time_axis = copy.deepcopy(time_axis)

        if isinstance(time_axis[0], datetime.datetime) == True:
            f_only_date = 1
            f_only_time = 1
            old_date    = ""
            old_time    = ""
            for idx, item in enumerate(time_axis):
                now_date = item.strftime("%Y-%m-%d")
                now_time = item.strftime("%H:%M:%S")
                if idx == 0:
                    old_date = now_date
                    old_time = now_time
                    continue
                if old_date != now_date:
                    f_only_date = 0
                if old_time != now_time:
                    f_only_time = 0

            if f_only_time == 1:
                time_format = "%Y-%m-%d"
            elif f_only_date == 1:
                time_format = "%H:%M:%S"
            else:
                time_format = "%d %H:%M:%S"

            for idx, item in enumerate(time_axis):
                time_axis[idx] = item.strftime(time_format)

        if isinstance(recodes[0], Iterable) == False:
            recodes = [recodes,]

        n_delete = 0
        o_size   = len(recodes[0])
        for idx in range(len(recodes[0])):
            if n_delete + idx >= o_size:
                break
            is_invalid = 0
            for axis_data in recodes:
                if axis_data[idx] == -1:
                    is_invalid = 1
                    break
            if is_invalid == 1:
               del time_axis[idx]
               for axis_data in recodes:
                    del axis_data[idx]
               n_delete += 1
                
        function_name, str_js = bulder.build_chart(recodes, time_axis, self.idx, title_axis, title)

        if function_name == None or str_js == None:
            return False
        
        self.str_js.append(str_js)
        self.function_name.append(function_name)

        return True

    def build_chart(self, html_name=None, group=None, is_show=False):
        if group != None:
            dirname = self.html_path + '/' + group
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
        else:
            dirname = self.html_path

        if html_name == None:
            html_name = get_now_time("%Y%m%d_%H%M%S_%f.html")

        file_name = "%s/%s" % (dirname, html_name)

        str_html  = '<html>\n'
        str_html += '  <head>\n'
        str_html += '   <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\n'
        str_html += '   <script type="text/javascript">\n'
        str_html += "     google.charts.load('current', {'packages':['corechart']});\n"
        for function_name in self.function_name:
            str_html += "     google.charts.setOnLoadCallback(%s);\n" % function_name
        for str_js in self.str_js:
            str_html += "     %s\n" % str_js
        str_html += "    </script>\n"
        str_html += "  </head>\n"
        str_html += "  <body>\n"
        for function_name in self.function_name:
            str_html += '    <div id="'+ function_name +'" style="width: 100%; height: 500px;"></div>\n'
        str_html += "  </body>\n"
        str_html += "</html>\n"
         
        #str_html = str_html.replace("\n", "\r\n")

        fd = open(file_name, "w")
        fd.write(str_html)
        fd.close()

        if is_show == True:
            os.commend(self.browser_name + " " + file_name + " &")
 
        self.idx           = 0       
        self.str_js        = []
        self.function_name = []

        return True








