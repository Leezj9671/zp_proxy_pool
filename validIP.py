import logging
logging.basicConfig(level=logging.INFO, filename='./logs/IPfailed.log')

from threading import Thread
import time
import concurrent.futures

import requests

from conf import CHECK_IP_ADD, REDIS_VALID_SET_NAME, REDIS_RAW_SET_NAME, CHECK_TIMES, REQUESTS_TIMEOUT, CHECK_MAX_WORKERS
from db import RedisClient


class CheckIP():

    def __init__(self):
        '''
        初始化IP检查地址和锚点IP
        '''
        self.check_url = CHECK_IP_ADD
        self.local_ip = self.update_local_ip()
        self.valid_redis_cli = RedisClient(REDIS_VALID_SET_NAME)
        self.raw_redis_cli = RedisClient(REDIS_RAW_SET_NAME)
        self.valid_proxypool = []
        self.wasted_proxy = []

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
                self.valid_redis_cli.save(curl)
                print('[√]{} is ok. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.valid_proxypool.append(curl)
            else:
                print('[!]{} is bad. Usedtime {:.2f}s'.format(curl, endtime - starttime))
                self.wasted_proxy.append(curl)
        except:
            print('[!]{} is bad. Exception occured.  Usedtime {:.2f}s'.format(curl, time.clock() - starttime))
            self.wasted_proxy.append(curl)

    def update_local_ip(self):
        '''
        更新锚点IP
        '''
        try:
            self.local_ip = requests.get(self.check_url).text
        except:
            logging.error('Can not access check IP:{}'.format(self.check_url))

    def threads_check_ip(self, iplist):
        '''
        启用多线程验证ip，移除无效代理
        iplist: <list> 待检查ip列表
        '''
        start_time_1 = time.clock()
        with concurrent.futures.ThreadPoolExecutor(max_workers=CHECK_MAX_WORKERS) as executor:
            for ip in iplist:
                executor.submit(self._check_ip, ip)
        print("Thread pool execution in " + str(time.clock() - start_time_1) + " seconds")
        self.raw_redis_cli.remove(*self.wasted_proxy)
        self.valid_redis_cli.save(*self.valid_proxypool)
        self.valid_proxypool.clear()
        self.wasted_proxy.clear()


def main():
    b = RedisClient()
    print(b.size)
    # check = CheckIP()
    # iplst = b.getN(b.size)
    # check.threads_check_ip(iplst)


if __name__ == '__main__':
    main()