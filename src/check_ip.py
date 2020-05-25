"""
1. Print改为logger
2. 一次性获取IP过多问题
"""


import logging
logging.basicConfig(level=logging.INFO, filename='./logs/IPfailed.log')

from threading import Thread
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from src.conf import CHECK_IP_ADD, REDIS_VALID_SET_NAME, REDIS_RAW_SET_NAME, REQUESTS_TIMEOUT, CHECK_MAX_WORKERS
from src.db import RedisClient


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
        curl_protocol = curl.split('://')[0]
        curl_link = curl.split('://')[1]
        if curl_protocol == 'socks5h':
            proxy = {
                'http': curl,
                'https': curl
            }
        else:
            proxy = {
                curl_protocol: curl_link
            }
        # starttime = time.process_time()
        try:
            retip = requests.get(self.check_url, proxies=proxy, timeout=REQUESTS_TIMEOUT)
            # 应该加一个返回状态判断
            # endtime = time.process_time()
            if retip.text != self.local_ip:
                # self.valid_redis_cli.save(curl)
                # print('[√]{} is ok. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.valid_proxypool.append(curl)
            else:
                # print('[!]{} is bad. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.wasted_proxy.append(curl)
        except Exception as e:
            # print('[!]{} is bad. Exception occured.  Usedtime {:.2f}s'.format(curl, time.process_time() - starttime))
            self.wasted_proxy.append(curl)

    def _update_local_ip(self):
        '''
        更新锚点IP
        '''
        while True:
            try:
                self.local_ip = requests.get(self.check_url).text
            except:
                logging.error('Can not access check IP:{}, try again...'.format(self.check_url))
            else:
                break

    def threads_check_ip(self, iplist=None, threads_num=CHECK_MAX_WORKERS):
        '''
        启用多线程验证ip，移除无效代理
        iplist: <list> 待检查ip列表
        '''
        self._update_local_ip()
        if not iplist:
            iplist = self.raw_redis_cli.get_all()
        if self.raw_redis_cli.size == 0:
            return
        start_time_1 = time.process_time()
        with ThreadPoolExecutor(max_workers=threads_num) as executor:
            for ip in iplist:
                executor.submit(self._check_ip, ip)
        self.raw_redis_cli.remove(self.wasted_proxy + self.valid_proxypool)
        self.valid_redis_cli.save(self.valid_proxypool)
        self.valid_proxypool.clear()
        self.wasted_proxy.clear()


def valid_ip_process(from_db=REDIS_VALID_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    valid_db = RedisClient(to_db)
    valid_db_size = valid_db.size
    if valid_db_size > 0:
        start_time = time.perf_counter()
        check = CheckIP(from_db=from_db, to_db=to_db)
        check.threads_check_ip()
        print('Checked valid proxy pool. Valid IP counts before: {}->{}, used time: {:.4f} seconds'.format(valid_db_size, valid_db.size, time.perf_counter() - start_time))
        logging.info('Checked valid proxy pool. Valid IP counts before: {}->{}, used time: {:.4f} seconds'.format(valid_db_size, valid_db.size, time.perf_counter() - start_time))


def raw_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    start_time = time.perf_counter()
    raw_db = RedisClient(from_db)
    valid_db = RedisClient(to_db)
    raw_db_size = raw_db.size
    if raw_db_size == 0:
        logging.info('Checked raw IP proxy pool. No ip in it now.')
    else:
        valid_db_size = valid_db.size
        check = CheckIP(from_db=from_db, to_db=to_db)
        check.threads_check_ip()
        print('Checked raw IP proxy pool.Raw IP counts:{}, valid IP counts before: {}, after: {}, used time: {:.4f} seconds'.format(raw_db_size, valid_db_size, valid_db.size, time.perf_counter() - start_time))
        logging.info('Checked raw IP proxy pool.Raw IP counts:{}, valid IP counts {}->{}, used time: {:.4f} seconds'.format(raw_db_size, valid_db_size, valid_db.size, time.perf_counter() - start_time))


if __name__ == '__main__':
    #测试代码
    # b = RedisClient(REDIS_RAW_SET_NAME)
    # c = RedisClient(REDIS_VALID_SET_NAME)
    # while True:
    #     check = CheckIP(from_db=REDIS_VALID_SET_NAME, to_db=REDIS_VALID_SET_NAME)
    #     check.threads_check_ip()
    #     print('raw:{}  valid:{}'.format(b.size, c.size))

    valid_ip_process()
    raw_ip_process()
