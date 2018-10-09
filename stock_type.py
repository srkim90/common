# -*- coding: utf-8 -*-

'''
  Author   " Kim, Seongrae
  Filename " main.py
  Release  " 1
  Date     " 2018-08-26
 
  Description " Stock HIS Main module
 
  Notes "
  ===================
  History
  ===================
  2018/08/26  created by Kim, Seongrae
'''

import os
import sys
from time import sleep
from singleton import *

#common
def get_python_type(c_type):
    c_type = c_type.replace(" or ", ",")
    c_type = c_type.replace(" ", "")
    c_type = c_type.split(',')

    type_list = []

    for __type in c_type:
        if c_type == "string" or c_type == "char":
            if str not in type_list:
                type_list.append(str)
        elif c_type == "float" or c_type == "double":
            if float not in type_list:
                type_list.append(float)
        else:
            if int not in type_list:
                type_list.append(int)
    if len(type_list) == 1:
        return type_list[0]
    else:
        return tuple(type_list)

def detect_data_type(data):
    n_dot = 0
    n_number = 0
    n_non_number = 0
    for ch in data:
        _ord = ord(ch)
        if ch == '0':
            n_dot += 1
            continue
        elif _ord >= ord('0') and _ord <= ord('9'):
            n_number += 1
            continue
        else:
            n_non_number += 1
            continue   

    if n_number != 0 and n_dot == 0 and n_non_number == 0:
        return int
    elif n_number != 0 and n_dot == 1 and n_non_number == 0:
        return float
    return str

#StockMst2
dict_of_StockMst2 = [
        [0  , "string"          , "종목 코드"                   ],
        [1  , "string"          , "종목명"                      ],
        [2  , "long"            , "시간(HHMM)"                  ],
        [3  , "long"            , "현재가"                      ],
        [4  , "long"            , "전일대비"                    ],
        [5  , "char"            , "상태구분"                    ],
        #'''# 상태구분
        #        '1' 상한
        #        '2' 상승
        #        '3' 보합
        #        '4' 하한
        #        '5' 하락
        #        '6' 기세상한
        #        '7' 기세상승
        #        '8' 기세하한
        #        '9' 기세하락
        #'''
        [6  , "long"            , "시가"                        ],
        [7  , "long"            , "고가"                        ],
        [8  , "long"            , "저가"                        ],
        [9  , "long"            , "매도호가"                    ],
        [10 , "long"            , "매수호가"                    ],
        [11 , "unsigned long"   , "거래량 [주의] 단위 1주"      ],
        [12 , "long"            , "거래대금 [주의] 단위 천원"   ],
        [13 , "long"            , "총매도잔량"                  ],
        [14 , "long"            , "총매수잔량"                  ],
        [15 , "long"            , "매도잔량"                    ],
        [16 , "long"            , "매수잔량"                    ],
        [17 , "unsigned long"   , "상장주식수"                  ],
        [18 , "long"            , "외국인보유비율(%)"           ],
        [19 , "long"            , "전일종가"                    ],
        [20 , "unsigned long"   , "전일거래량"                  ],
        [21 , "long"            , "체결강도"                    ],
        [22 , "unsigned long"   , "순간체결량"                  ],
        [23 , "char"            , "체결가비교 Flag"             ],
        #'''# 체결가비교
        #        'O' 매도
        #        'B' 매수
        #'''
        [24 , "char"            , "호가비교 Flag"               ],
        #'''# 호가비교
        #        'O' 매도
        #        'B' 매수
        #'''
        [25 , "char"            , "동시호가구분"                ],
        #'''# 동시호가구분
        #        '1' 동시호가
        #        '2' 장중
        #'''
        [26 , "long"            , "예상체결가"                  ],
        [27 , "long"            , "예상체결가 전일대비"         ],
        [28 , "long"            , "예상체결가 상태구분"         ],
        #'''# 예상체결가 상태구분
        #        '1' 상한
        #        '2' 상승
        #        '3' 보합
        #        '4' 하한
        #        '5' 하락
        #        '6' 기세상한
        #        '7' 기세상승
        #        '8' 기세하한
        #        '9' 기세하락
        #'''
        [29 , "unsigned long"   , "예상체결가 거래량"           ],
    ]

def get_data_type_at_StockMst2(idx_type):
    for item in dict_of_StockMst2:
        if item[0] == idx_type:
            # type, description
            return (get_python_type(item[1]), item[2])

    return (None, None)

def make_stock_items_description_StockMst2(idx_list):
    all_of_description = "[description] "
    for item in idx_list:
        py_type, description = get_data_type_at_StockMst2(item)
        all_of_description += "%s," % description
    
    if all_of_description[-1] == ',':
        all_of_description = all_of_description[0:-1]

    return all_of_description



#StockChart
dict_of_StockChart = [
        [0  , "ulong"               , "날짜"                ],
        [1  , "long"                , "시간"                ], #- hhmm
        [2  , "long or float"       , "시가"                ],
        [3  , "long or float"       , "고가"                ],
        [4  , "long or float"       , "저가"                ],
        [5  , "long or float"       , "종가"                ],
        [6  , "long or float"       , "전일대비"            ], #- 주) 대비부호(37)과 반드시 같이 요청해야 함
        [8  , "ulong or ulonglong"  , "거래량"              ], #- 주) 정밀도 만원 단위
        [9  , "ulonglong"           , "거래대금"            ],
        [10 , "ulong or ulonglong"  , "누적체결매도수량"    ], #- 호가비교방식 누적체결매도수량
        [11 , "ulong or ulonglong"  , "누적체결매수수량"    ], #- 호가비교방식 누적체결매수수량
        [12 , "ulonglong"           , "상장주식수"          ],
        [13 , "ulonglong"           , "시가총액"            ],
        [14 , "ulong"               , "외국인주문한도수량"  ],
        [15 , "ulong"               , "외국인주문가능수량"  ],
        [16 , "ulong"               , "외국인현보유수량"    ],
        [17 , "float"               , "외국인현보유비율"    ],
        [18 , "ulong"               , "수정주가일자"        ], #- YYYYMMDD
        [19 , "float"               , "수정주가비율"        ],
        [20 , "long"                , "기관순매수"          ],
        [21 , "long"                , "기관누적순매수"      ],
        [22 , "long"                , "등락주선"            ],
        [23 , "float"               , "등락비율"            ],
        [24 , "ulonglong"           , "예탁금"              ],
        [25 , "float"               , "주식회전율"          ],
        [26 , "float"               , "거래성립률"          ],
        [37 , "char"                , "대비부호"            ], #- 수신값은 GetHeaderValue 8 대비부호와 동일
    ]

def get_data_type_at_StockChart(idx_type):
    for item in dict_of_StockChart:
        if item[0] == idx_type:
            # type, description
            return (get_python_type(item[1]), item[2])

    return (None, None)

def make_stock_items_description_StockChart(idx_list):
    all_of_description = "# description: "
    for item in idx_list:
        py_type, description = get_data_type_at_StockChart(item)
        all_of_description += "%s, " % description
    
    if all_of_description[-1] == ', ':
        all_of_description = all_of_description[0:-2]

    return all_of_description


