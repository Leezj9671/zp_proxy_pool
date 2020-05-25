import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/crawl_logger.log',
                    filemode='a')

import time
from concurrent import futures
from random import randint
import re

import requests
from bs4 import BeautifulSoup
from lxml import etree
from fake_useragent import UserAgent

from src.db import RedisClient


#Fake Useragent
ua = UserAgent()


class SpiderMeta(type):
    spiders = []
    rediscli = RedisClient()

    def _init(cls):
        pass

    def __new__(cls, *args, **kwargs):
        if 'getip' not in args[2]:
            logging.error('GetIP not in args, failed!')
            return None

        args[2]['__init__'] = lambda self: SpiderMeta._init(self)
        args[2]['save_to_db'] = lambda self, ip_list: SpiderMeta._save_to_db(self, ip_list)
        args[2]['get_html'] = lambda self, url: SpiderMeta._get_html(self, url)

        SpiderMeta.spiders.append(type.__new__(cls, *args, **kwargs))
        return type.__new__(cls, *args, **kwargs)

    def _save_to_db(cls, ip_list):
        SpiderMeta.rediscli.save(ip_list)

    def _get_html(cls, url):
        headers = {
            'User-Agent': ua.random
        }
        r = requests.get(url, headers=headers)
        try:
            soup = BeautifulSoup(r.content.decode("utf-8"), 'lxml')
        except UnicodeDecodeError:
            soup = BeautifulSoup(r.text, 'lxml')
        return soup

    # def _log_decorator(cls, func):
    #     def wrapper():
    #         start_time = time.perf_counter()
    #         func()
    #         logging.info('Crawled 66daili success in {}seconds, got crawled ip {}'.format(time.perf_counter()-start_time, len(ip_list)))
    #     return wrapper

class Daili66Spider(metaclass=SpiderMeta):
    start_url = 'http://www.66ip.cn/{}.html'

    def getip(self, page_num=15):
        urls = [self.start_url.format(i) for i in range(1, page_num+1)]
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            proxy_list = soup.find('table', {"border": "2px"})
            for proxy in proxy_list.find_all('tr')[1:]:
                alltd = proxy.find_all('td')
                ip_list.append('http://{}:{}'.format(alltd[0].string, alltd[1].string))
                ip_list.append('https://{}:{}'.format(alltd[0].string, alltd[1].string))
        logging.info('Crawled 66daili success, got crawled ip {}'.format(len(ip_list)))
        self.save_to_db(all_ip_list)


class KuaidailiSpider(metaclass=SpiderMeta):
    start_url = 'http://www.kuaidaili.com/free/inha/{}/'

    def getip(self, page_num=15):
        urls = [self.start_url.format(i) for i in range(1, page_num+1)]
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            proxy_list = soup.find('table', {'class': 'table table-bordered table-striped'}).find('tbody')
            for proxy in proxy_list.find_all('tr'):
                alltd = proxy.find_all('td')
                ip_list.append('{}://{}:{}'.format(alltd[3].string.lower(), alltd[0].string, alltd[1].string.lower()))
        logging.info('Crawled kuaidaili success, got crawled ip {}'.format(len(ip_list)))
        self.save_to_db(ip_list)


class XiciSpider(metaclass=SpiderMeta):
    """
    西刺代理
    """

    def getip(self, page_num=10):
        urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, page_num+1)]
        urls.extend(['https://www.xicidaili.com/nt/{}'.format(i) for i in range(1, page_num+1)])
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            try:
                alltr = soup.find(id="ip_list").findAll('tr')
            except:
                logging.error('Can not get table: {}'.format(url))
                continue
            for tr in alltr[1:]:
                alltd = tr.findAll('td')
                ip_list.append('{}://{}:{}'.format(alltd[5].string.lower(), alltd[1].string, alltd[2].string))
        logging.info('Crawled xicidaili success, got crawled ip {}'.format(len(ip_list)))
        self.save_to_db(ip_list)

class IP89Spider(metaclass=SpiderMeta):
    """
    89IP代理是API接口直接获取
    """

    def getip(self, page_num=None):
        # 随机个数取IP，否则可能被ban
        all_ip_list = []
        arealist = ['美国', '日本', '俄罗斯', '英国', '澳大利亚']
        for area in arealist:
            area_encode = requests.urllib3.util.parse_url(area)
            url = 'http://www.89ip.cn/tqdl.html?api=1&num={}&port=&address={}&isp='.format(randint(490, 510), area_encode)
            headers = {
                'User-Agent': ua.random
            }
            try:
                text = requests.get(url, headers=headers, timeout=10).text
            except:
                logging.error('89IP Can not get table: {}'.format(url))
                return None
            all_ip = re.findall('(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}\:\d{1,5}', text)
            all_ip_list.extend(list(map(lambda ip:'http://'+ip, all_ip)))
            all_ip_list.extend(list(map(lambda ip:'https://'+ip, all_ip)))
            all_ip_list.extend(list(map(lambda ip:'socks5h://'+ip, all_ip)))
            time.sleep(3)
        # print(all_ip_list)
        logging.info('Crawled 89daili success, got crawled ip {}'.format(len(all_ip_list)))
        self.save_to_db(all_ip_list)

class FineProxySpider(metaclass=SpiderMeta):
    '''
    Fineproxy
    http://fineproxy.org/eng/fresh-proxies
    '''

    def getip(self, page_num=None):
        url = 'http://fineproxy.org/eng/fresh-proxies'
        all_ip_list = []
        page_html = requests.get(url, headers={'User-Agent':ua.random}, timeout=10).text
        page_html.replace('<strong><font style="vertical-align: inherit;">：</font></strong>', ':')
        page_html.replace('。', '.')
        all_ip = re.findall('(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}\:\d{1,5}', page_html)
        all_ip_list.extend(list(map(lambda ip:'http://'+ip, all_ip)))
        all_ip_list.extend(list(map(lambda ip:'https://'+ip, all_ip)))
        all_ip_list.extend(list(map(lambda ip:'socks5h://'+ip, all_ip)))
        logging.info('Crawled FineProxy success, got crawled ip {}'.format(len(all_ip_list)))
        self.save_to_db(all_ip_list)


class QyProxySpider(metaclass=SpiderMeta):
    start_url = 'http://www.qydaili.com/free/?action=&page={}'

    def getip(self, page_num=15):
        urls = [self.start_url.format(i) for i in range(1, page_num+1)]
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            proxy_list = soup.find('table', {'class': 'table table-bordered table-striped'}).find('tbody')
            for proxy in proxy_list.find_all('tr'):
                alltd = proxy.find_all('td')
                if alltd[0].string and alltd[1].string and alltd[3].string:
                    ip_list.append('{}://{}:{}'.format(alltd[3].string.lower(), alltd[0].string, alltd[1].string.lower()))
        logging.info('Crawled qydaili success, got crawled ip {}'.format(len(ip_list)))
        self.save_to_db(ip_list)


def main():
    spiders = [cls() for cls in SpiderMeta.spiders]
    with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
        for spider in spiders:
            executor.submit(spider.getip)

if __name__ == '__main__':
    main()
    # FineProxySpider().getip()
    # QyProxySpider().getip()
