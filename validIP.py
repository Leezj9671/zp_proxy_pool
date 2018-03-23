import logging
logging.basicConfig(level=logging.INFO, filename='./logs/IPfailed.log')

from threading import Thread
from time import time

import requests

from conf import CHECK_IP_ADD, REDIS_VALID_SET_NAME, REDIS_RAW_SET_NAME
from db import RedisClient

proxypool = []
wasted_proxy = []

class CheckIP(Thread):

    def __init__(self):
        '''
        初始化IP检查地址和锚点IP
        '''
        Thread.__init__(self)
        self.check_url = CHECK_IP_ADD
        self.local_ip = self.update_local_ip()
        self.validrediscli = RedisClient(REDIS_VALID_SET_NAME)
        self.rawrediscli = RedisClient(REDIS_RAW_SET_NAME)
        self.threads = []

    def _check_ip(self, curl):
        '''
        检测ip可用性
        curl: 待检测的ip地址。
        '''
        curl = curl.strip()
        proxy = {
            curl.split('://')[0]: curl
        }
        try:
            starttime = int(round(time() * 1000))
            retip = requests.get(self.check_url, proxies=proxy, timeout=2)
            endtime = int(round(time() * 1000))
            if retip.text != self.local_ip:
                self.validrediscli.save(curl)
                print('[√]{} is ok. Usedtime {}s'.format(
                    curl, (endtime - starttime) / 1000))
                proxypool.append(curl)
            else:
                print('[!]{} is bad. Usedtime {}s'.format(
                    curl, (endtime - starttime) / 1000))
                wasted_proxy.append(curl)
        except:
            print('[!]{} is bad. Exception occured'.format(curl))
            wasted_proxy.append(curl)

    def _check_lots_ip(self, curls):
        '''
        检测多个ip可用性
        curls: ip地址数组
        '''
        self.update_local_ip()
        for curl in curls:
            self._check_ip(curl)
        if wasted_proxy != []:
            self.rawrediscli.remove(*wasted_proxy)

    def update_local_ip(self):
        '''
        更新锚点IP
        '''
        self.local_ip = requests.get(self.check_url).text

    def threads_check_ip(self, iplist):
        '''
        启用多线程查看ip
        iplist: 待检查ip列表
        '''
        pass

def main():
    b = RedisClient()
    print(b.size)
    testp = b.getN(50)
    a = CheckIP()
    a._check_lots_ip(testp)
    print(b.size)

if __name__ == '__main__':
    main()