# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : __init__.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : common module entry
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''

# common package import
import re
import os
import sys
import pytz
import json
import redis
import timeit
import threading
from time import *
from datetime import *

# custom package import
from .log import *
#from .gui import *
from .util import *
from .param import *
from .config import *
from .redis_db import *
from .cap_list import *
from .mmc_parse import *
from .singleton import *
from .stock_type import *
from .ftp_client import *
from .google_chart import *
from .signal_handler import *
#from .dispatch_parse import *
# custom literal define
OS_TYPE = get_os_type()
if "STOCK_HOME" in os.environ:
    STOCK_HOME=os.environ["STOCK_HOME"]
elif OS_TYPE == OS_TYPE_WINDOW:
    STOCK_HOME="C:\\Users\\root\\Downloads\\src"
else: # LINUX
    STOCK_HOME="/home/seongrae/stock"


# init custom package
init_param()
init_signal()
