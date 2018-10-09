# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : db.py
  Release  : 1
  Date     : 2018-08-12
 
  Description : redis handling module
  
  Notes :
  ===================
  History
  ===================
  2018/08/12  created by Kim, Seongrae
'''
import os
import sys
import redis
import threading
from time import sleep

from log import *
from singleton import *
from multiprocessing.pool import Pool

THRESHOLD_LOCAL_HANDLE = 50

DEFAULT_REDIS_CONNECTION=8

DB_UPDATE_FLAGS_NONE        = 0
DB_UPDATE_FLAGS_OVERWRITE   = 1
DB_UPDATE_FLAGS_APPEND      = 2

class redis_db(singleton_instance):
    TPS               = 0
    rr_index          = 0
    f_exit            = False
    h_redis           = []
    local_queue_del   = []
    local_queue_key   = []
    local_queue_val   = []
    local_queue_flags = []
    local_lock        = threading.Semaphore(1)
    def __init__(self, host_ipaddr, host_port, host_passwd, n_conn=DEFAULT_REDIS_CONNECTION):
        self.working     = 0
        self.host_ipaddr = host_ipaddr
        self.host_port   = host_port
        self.host_passwd = host_passwd
        self.n_conn      = n_conn
        self.h_redis     = [ None for i in range(self.n_conn)]
        self.lock        = [ threading.Semaphore(1) for i in range(self.n_conn)]
        self.proc_pool   = Pool(processes=n_conn)
        self.base_lock   = threading.Semaphore(n_conn)

        hThread = threading.Thread(target=self._connection_watchdog_th)
        hThread.daemon = True
        hThread.start()

        hThread = threading.Thread(target=self._local_work_th)
        hThread.daemon = True
        hThread.start()

        hThread = threading.Thread(target=self._local_stat_th)
        hThread.daemon = True
        hThread.start()

        sleep(0.5)
    
    def get_running_proc(self):
        return self.working

    def del_data(self, key):
        if type(key) != list:
            key  = list(key)

        if len(key) < THRESHOLD_LOCAL_HANDLE:
            self.local_lock.acquire()
            self.local_queue_del   += key
            self.local_lock.release()
            return True

        self.base_lock.acquire()

        if key == None or len(key) == 0:
            self.base_lock.release()
            return False

        hThread = threading.Thread(target=self._db_join_th, args=(key, None, None))
        hThread.daemon = True
        hThread.start()

        return True
 

    def push_data(self, key, data, update_flags):
        if type(key) != list:
            key  = list(key)
            data = list(data)

        if len(key) != len(data):
            PRINT("[push_data] Error!! Invalid Input parameters: len(key) != len(data)")
            return False
                    
        flags = [update_flags] * len(key)
        if len(key) < THRESHOLD_LOCAL_HANDLE:
            self.local_lock.acquire()
            self.local_queue_key   += key
            self.local_queue_val   += data
            self.local_queue_flags += flags
            self.local_lock.release()
            return True

        self.base_lock.acquire()

        if data == None or len(data) == 0:
            self.base_lock.release()
            return False

        hThread = threading.Thread(target=self._db_join_th, args=(key, data, flags))
        hThread.daemon = True
        hThread.start()

        return True
    
    def get_data(self, key):
        handle = None
        while handle == None:
            index  = self._get_rr_index()
            handle = self.h_redis[index]
            
            break
            #print("!!!!!!!!!!!")
            #sleep(0.01)

        self.lock[index].acquire()
        lrange_list = handle.lrange(key, 0, -1)
        self.lock[index].release()

        for idx, item in enumerate(lrange_list):
            if type(item) == bytes:
                lrange_list[idx] = item.decode('utf-8')
        return lrange_list

    def _local_stat_th(self):
        while True:
            sleep(1)
            self.local_lock.acquire()
            TPS      = self.TPS
            self.TPS = 0
            self.local_lock.release()

            #print("DB TPS : %d" % (TPS))

    def _local_work_th(self):
        sleep(0.01)
        while True:
            self.local_lock.acquire()
            local_queue_key   = self.local_queue_key
            local_queue_val   = self.local_queue_val
            local_queue_flags = self.local_queue_flags
            local_queue_del   = self.local_queue_del
            self.local_queue_key   = []
            self.local_queue_val   = []
            self.local_queue_flags = []
            self.local_queue_del   = []
            self.local_lock.release()
            #print("aaaa")
    
            if len(local_queue_del) != 0:
                self._push_data(self.h_redis[0], local_queue_del, None, local_queue_flags)
                
            if len(local_queue_key) > (THRESHOLD_LOCAL_HANDLE + 1) * 10:
                self.push_data(local_queue_key, local_queue_val, local_queue_flags)
                #print("bbbb")
                continue

            if len(local_queue_key) == 0 or self.h_redis[0] == None:
                sleep(0.05)
                continue

            #print("cccc")
            self._push_data(self.h_redis[0], local_queue_key, local_queue_val, local_queue_flags)

    def _db_join_th(self, key, data, flags):
        #print ("start!!! ")
        self.working += 1
        hProc = self.proc_pool.apply_async(redis_db._push_data, [None, key, data, flags, (self.host_ipaddr, self.host_port, self.host_passwd)])
        ret = hProc.get()
        self.TPS += len(key)
        #print ("end!!! %s" % (ret))
        #self.lock[idx].release()
        self.working -= 1
        self.base_lock.release()
        return ret

    @staticmethod
    def _push_data(db_handle, key, data, flags, db_info=None):
        now_handle = None
        if db_handle == None:
            #now_handle = redis_db._connect(self, db_info=db_info)
            now_handle = redis_db._connect_s(db_info=db_info)
        else:
            now_handle = db_handle
        #print("db_handle:%s, key:%s, data:%s" % (db_handle, key, data))
        for i in range(len(key)):
            #print ("key=%s, value=%s" % (key[i], data[i]))
            if data == None:
                if now_handle.exists(key[i]) == 1:
                    now_handle.delete(key[i])
                continue
            elif type(data[i]) != list:
                record = [data[i]]
            else:
                record = data[i]

            if now_handle.exists(key[i]) != 1:
                pass # DB에 해당 Key 가 없을 경우
            elif flags[i] == DB_UPDATE_FLAGS_OVERWRITE:
                now_handle.delete(key[i])#DB에 해당 Key 가 있지만, 덮어쓰기가 활성화 되어 있을 경우
            elif flags[i] == DB_UPDATE_FLAGS_APPEND:
                pass #DB에 해당 Key 가 있지만, 이어 쓰기가 활성화
            elif flags[i] == DB_UPDATE_FLAGS_NONE:
                continue#DB에 해당 Key 가 있어서 쓰지 않음
                
            for item in record:
                #print("now_handle:%s , type:%s" % (now_handle, type(now_handle)))
                #print("rpush: %s, %s" % (key[i], item))
                now_handle.rpush(key[i], item)
        
        if db_handle == None:
            #now_handle.close()
            now_handle.connection_pool.disconnect()
        return True
    '''

    def set_data(self, key, data):
        if data == None or len(data) == 0 or self.h_redis == None:
            return
        self.h_redis.set(key, data)

    def get_data(self, key):
        if self.h_redis == None:
            return None
        #self.h_redis.keys()
        return self.h_redis.get(key)
    '''

    def _connection_watchdog_th(self):
        while self.f_exit == False:
            for i in range (self.n_conn):
                #PRINT("self.h_redis[i]=%s" % self.h_redis[i])
                if self.h_redis[i] == None:
                    if self._connect(i) != False:
                        #PRINT("Redis Connection on! : host_ipaddr=%s, host_port=%s, idx=%d" % (self.host_ipaddr, self.host_port, i))
                        LOG(LOG_CRT, "Redis Connection on! : host_ipaddr=%s, host_port=%s, idx=%d" % (self.host_ipaddr, self.host_port, i))
                    else:
                        PRINT("Redis Conn fail : idx=%d" % (i))
                else:
                    try:
                        response = self.h_redis[i].client_list()
                    except redis.ConnectionError:
                        LOG(LOG_CRT, "Redis Connection down! : host_ipaddr=%s, host_port=%s, idx=%d" % (self.host_ipaddr, self.host_port, i))
                        #PRINT("Redis Connection down! : host_ipaddr=%s, host_port=%s, idx=%d" % (self.host_ipaddr, self.host_port, i))
                        self.h_redis[i].close()
                        self.h_redis[i] = None

            sleep(1.0)


    @staticmethod
    def _connect_s(db_info):
        try:
            h_ret = redis.Redis(
                            host=db_info[0],
                            port=db_info[1], 
                            password=db_info[2])
        except:
            return False
        return h_ret
 

    def _connect(self, idx=-1, db_info=None):
        '''
        if self != None:
           print("%s,%s,%s" % (self.host_ipaddr, self.host_port, self.host_passwd))
        else:
           print("%s,%s,%s" % (db_info[0], db_info[1], db_info[2]))
        '''
        try:
            if self != None:
                h_ret = redis.Redis(
                                host=self.host_ipaddr,
                                port=self.host_port, 
                                password=self.host_passwd)
            elif db_info != None:
                h_ret = redis.Redis(
                                host=db_info[0],
                                port=db_info[1], 
                                password=db_info[2])
            if idx >= 0:
                self.h_redis[idx] = h_ret
        except:
            if idx >= 0:
                self.h_redis[idx] = None
            return False
        return h_ret
    
    def _get_rr_index(self):
        self.local_lock.acquire()
        index = self.rr_index % self.n_conn
        self.rr_index +=1
        self.local_lock.release()

        return index
        

    def get_handle(self, idx=0):
        return self.h_redis[idx]

def redis_push_data(key, data, update_flags):
    db = redis_db.getinstance()
    db.push_data(key, data, update_flags)

def redis_del_data(key):
    db = redis_db.getinstance()
    db.del_data(key)




