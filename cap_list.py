# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : main.py
  Release  : 1
  Date     : 2018-08-26
 
  Description : Stock HIS Main module
 
  Notes :
  ===================
  History
  ===================
  2018/08/26  created by Kim, Seongrae
'''

import os
import sys
import json
from time import sleep
from singleton import *

if sys.version_info[0] == 2:
    from io import open

cap_item =  [
        # Idx, Name                                 , Disc             , Default?
        [ 0  , "name"                               , "종목명"         , True       , str   ],
        [ 1  , "now_val"                            , "현재가"         , True       , int   ],
#       [ 2  , "yday_rate"                          , "전일비"         , True       , float ],
#       [ 3  , "rate"                               , "등락률"         , True       , float ],
        [ 2  , "par"                                , "액면가"         , True       , int   ],
        [ 3  , "quant"                              , "거래량"         , False      , int   ],
        [ 4  , "amount"                             , "거래대금"       , False      , int   ],
        [ 5  , "prev_quant"                         , "전일거래량"     , False      , int   ],
        [ 6  , "open_val"                           , "시가"           , False      , int   ],
        [ 7  , "high_val"                           , "고가"           , False      , int   ],
        [ 8  , "low_val"                            , "저가"           , False      , int   ],
        [ 9  , "ask_buy"                            , "매수호가"       , False      , int   ],
        [ 10 , "ask_sell"                           , "매도호가"       , False      , int   ],
        [ 11 , "buy_total"                          , "매수총잔량"     , False      , int   ],
        [ 12 , "sell_total"                         , "매도총잔량"     , False      , int   ],
        [ 13 , "listed_stock_cnt"                   , "상장주식수"     , False      , int   ],
        [ 14 , "market_sum"                         , "시가총액"       , False      , int   ],
        [ 15 , "sales"                              , "매출액"         , False      , int   ],
        [ 16 , "property_total"                     , "자산총계"       , False      , int   ],
        [ 17 , "debt_total"                         , "부채총계"       , False      , int   ],
        [ 18 , "operating_profit"                   , "영업이익"       , False      , int   ],
        [ 19 , "net_income"                         , "당기순이익"     , False      , int   ],
        [ 20 , "eps"                                , "주당순이익"     , False      , int   ],
        [ 21 , "dividend"                           , "보통주배당금"   , False      , int   ],
        [ 22 , "sales_increasing_rate"              , "매출액증가율"   , False      , float ],
        [ 23 , "operating_profit_increasing_rate"   , "영업이익증가율" , False      , float ],
        [ 24 , "frgn_rate"                          , "외국인비율"     , False      , float ],
        [ 25 , "per"                                , "PER"            , False      , float ],
        [ 26 , "roe"                                , "ROE"            , False      , float ],
        [ 27 , "roa"                                , "ROA"            , False      , float ],
        [ 28 , "pbr"                                , "PBR"            , False      , float ],
        [ 29 , "reserve_ratio"                      , "유보율"         , False      , float ] # can N/A

        #code, ranking, abnormal

    ]     
          


class CapInfo(singleton_instance):
    cap_list = []

    def __init__(self, cap_file_path, business_day_path=None, n_cut_off=-1, s_idx=-1, e_idx=-1):
        self.cap_file_path = cap_file_path
        self.business_day_path = business_day_path
        self.n_cut_off = n_cut_off
        self.s_idx = s_idx
        self.e_idx = e_idx
        self._load_cap()
        self.business_day_list = []
        if business_day_path != None:
            self._load_business_day()

    def _load_business_day(self):
        print("path: %s" % self.business_day_path)
        self.business_day_list = []
        for line in open(self.business_day_path, 'r', encoding='UTF8').readlines():
            line = line.split('#')[0]
            line = line.replace(" ",'')
            line = line.replace("\r",'')
            line = line.replace("\n",'')

            if len(line) != 10:
                continue
            #print("%s" % line)
            self.business_day_list.append(line)

        self.business_day_list = list(reversed(self.business_day_list))

        return self.business_day_list

    def _load_cap(self):
        print("path: %s" % self.cap_file_path)
        for line in open(self.cap_file_path, 'r', encoding='UTF8').readlines():
            line = line.split('#')[0]
            '''
            line = line.replace(']','[')
            line = line.replace("'",'')
            line = line.replace(" ",'')
            line = line.split('[')

            #print (len(line))
            if len(line) <= 1:
                continue
            line = line[1].split(',')

            if len(line) != 11:
                continue

           #[2, 'SK하이닉스', 75400, 5000, 548914, 728002, 50.3, 3631928, 5.16, 36.8, '000660']
            line[0] = int(line[0])      # 0: idx
                                        # 1: name
            line[2] = int(line[2])      # 2: price
            line[3] = int(line[3])      # 3: 액면가
            line[4] = int(line[4])      # 4: 시가총액
            line[5] = int(line[5])      # 5: 상장주식수
            line[6] = float(line[6])    # 6: 외국인비율
            line[7] = int(line[7])      # 7: 거래량
            line[8] = float(line[8])    # 8: PER
            line[9] = float(line[9])    # 9: ROE
                                        #10: code
            '''
            line = json.loads(line)
            self.cap_list.append(line)

        len_of_list = len(self.cap_list)
        if len_of_list > self.n_cut_off and self.n_cut_off != -1:
            self.cap_list = self.cap_list[0:self.n_cut_off]
        elif self.s_idx != -1 and self.e_idx != -1:
            if len_of_list > self.s_idx and len_of_list > self.e_idx:
                self.cap_list = self.cap_list[self.s_idx:self.e_idx]
            elif len_of_list > self.s_idx and len_of_list <= self.e_idx:
                self.cap_list = self.cap_list[self.s_idx:]
            else:
                self.cap_list = self.cap_list[0:]
        else:
            self.cap_list = self.cap_list[0:]

        return self.cap_list

    def get_code_list(self):
        codes = []
        for item in self.cap_list:
            codes.append(item["code"])
        return codes

    def get_selected_code_list(self):
        codes = []
        for item in self.cap_list:

            if item["abnormal"] == True:
                continue

            '''
            if item["per"] < 1.0 :
                continue
 

            if item[""] == :
                continue
 

            if item[""] == :
                continue
 

            if item[""] == :
                continue
            '''

            codes.append(item["code"])
        return codes       

    def get_business_day_list(self):
        #2018.08.01
        return self.business_day_list[0:]

    def get_business_day_list2(self):
        #["2018", "08", "01"]
        result = []
        for item in self.business_day_list:
            item = item.split(".")
            for idx, date in enumerate(item):
                item[idx] = int(date)
            result.append(item)

        return result
        
    def get_business_day_n_before(self, str_day, n_day_before=1, n_day_ago=None): # yymmdd or yyyymmdd, or yy.mm.dd or yyyy.mm.dd or yy:mm:dd or yyyy:mm:dd or yy-mm-dd or yyyy-mm-dd or yy_mm_dd or yyyy_mm_dd or
        str_day = str_day.replace('.', '')
        str_day = str_day.replace('-', '')
        str_day = str_day.replace('_', '')
        str_day = str_day.replace(':', '')

        day_add = (n_day_before * 1) if n_day_before != None else (n_day_ago * -1)

        if len(str_day) == 6:
            if int(str_day[0:2]) < 60:
                str_day = "20" + str_day
            else:
                str_day = "19" + str_day
        elif len(str_day) == 8:
            pass
        else:
            return -1

        for idx, item in enumerate(self.business_day_list):
            item = item.split(".")
            it_day = "%s%s%s" % (item[0], item[1], item[2])

            if it_day == str_day:
                try:
                    #print("idx:%d , day_add:%d" % (idx, day_add))
                    result_list = self.business_day_list[idx + day_add].split(".")
                except Exception as e:
                    #print("%s, %s" % (it_day , day_add))
                    result_list = None

                #return : ["2018", "08", "01"]
                return result_list
                    
        return None 

    def find_stock_infor_by_code(self, code):
        for item in self.cap_list:
            if code == item["code"]:
                return item
        return None

def get_stock_name_by_code(code):
    e   = CapInfo.getinstance()
    cap = e.find_stock_infor_by_code(code)
    if cap == None:
        return "None"
    return cap["name"]





