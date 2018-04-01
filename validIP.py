"""
1. Print改为logger
2. 
"""


import logging
logging.basicConfig(level=logging.INFO, filename='./logs/IPfailed.log')

from threading import Thread
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from conf import CHECK_IP_ADD, REDIS_VALID_SET_NAME, REDIS_RAW_SET_NAME, CHECK_TIMES, REQUESTS_TIMEOUT, CHECK_MAX_WORKERS
from db import RedisClient


class CheckIP():

    def __init__(self, from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
        '''
        初始化IP检查地址和锚点IP
        :param from_db: 取出的数据库
        :param to_db: 验证后存储的数据库
        '''
        self.check_url = CHECK_IP_ADD
        self.local_ip = None
        self.valid_redis_cli = RedisClient(to_db)
        self.raw_redis_cli = RedisClient(from_db)
        self.valid_proxypool = []
        self.wasted_proxy = []
        self._update_local_ip()

    def _check_ip(self, curl):
        '''
        检测ip可用性
        curl: 待检测的ip地址。
        '''
        curl = curl.strip()
        proxy = {
            curl.split('://')[0]: curl
        }
        starttime = time.clock()
        try:
            retip = requests.get(self.check_url, proxies=proxy, timeout=REQUESTS_TIMEOUT)
            # 应该加一个返回状态判断
            endtime = time.clock()
            if retip.text != self.local_ip:
                # self.valid_redis_cli.save(curl)
                print('[√]{} is ok. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.valid_proxypool.append(curl)
            else:
                print('[!]{} is bad. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.wasted_proxy.append(curl)
        except Exception as e:
            print('[!]{} is bad. Exception occured.  Usedtime {:.2f}s'.format(curl, time.clock() - starttime))
            self.wasted_proxy.append(curl)

    def _update_local_ip(self):
        '''
        更新锚点IP
        '''
        try:
            self.local_ip = requests.get(self.check_url).text
        except:
            logging.error('Can not access check IP:{}'.format(self.check_url))
            self.local_ip = None

    def threads_check_ip(self, iplist=None):
        '''
        启用多线程验证ip，移除无效代理
        iplist: <list> 待检查ip列表
        '''
        self._update_local_ip()
        if not iplist:
            iplist = self.raw_redis_cli.get_all()
        if self.raw_redis_cli.size == 0:
            print('no proxy')
            return
        start_time_1 = time.clock()
        with ThreadPoolExecutor(max_workers=CHECK_MAX_WORKERS) as executor:
            for ip in iplist:
                executor.submit(self._check_ip, ip)
        print("Check thread pool execution in {:.4f} seconds".format(time.clock() - start_time_1))
        self.raw_redis_cli.remove(self.wasted_proxy + self.valid_proxypool)
        self.valid_redis_cli.save(self.valid_proxypool)
        self.valid_proxypool.clear()
        self.wasted_proxy.clear()


if __name__ == '__main__':
    b = RedisClient(REDIS_RAW_SET_NAME)
    c = RedisClient(REDIS_VALID_SET_NAME)
    print('raw:{}  valid:{}'.format(b.size, c.size))
    check = CheckIP(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME)
    check.threads_check_ip()
    print('raw:{}  valid:{}'.format(b.size, c.size))