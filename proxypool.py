import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/crawl_logger.log',
                    filemode='a')

import time
from concurrent import futures

import requests
from bs4 import BeautifulSoup

from db import RedisClient

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}



class SpiderMeta(type):
    spiders = []

    def _init(cls):
        pass

    def __new__(cls, *args, **kwargs):
        if 'getip' not in args[2]:
            print('error')

        args[2]['__init__'] = lambda self: SpiderMeta._init(self)
        args[2]['save_to_db'] = lambda self, ip_list: SpiderMeta._save_to_db(self, ip_list)
        args[2]['get_html'] = lambda self, url: SpiderMeta._get_html(self, url)

        SpiderMeta.spiders.append(type.__new__(cls, *args, **kwargs))
        return type.__new__(cls, *args, **kwargs)

    def _save_to_db(cls, ip_list):
        rediscli = RedisClient()
        rediscli.save(ip_list)

    def _get_html(cls, url):
        r = requests.get(url, headers=headers)
        try:
            soup = BeautifulSoup(r.content.decode("utf-8"), 'lxml')
        except UnicodeDecodeError:
            soup = BeautifulSoup(r.text, 'lxml')
        return soup

class Daili66Spider(metaclass=SpiderMeta):
    start_url = 'http://www.66ip.cn/{}.html'

    def getip(self, page_num=5):
        # print('crawling 666')
        urls = [self.start_url.format(i) for i in range(1, page_num+1)]
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            proxy_list = soup.find('table', {"border": "2px"})
            for proxy in proxy_list.find_all('tr')[1:]:
                alltd = proxy.find_all('td')
                ip_list.append('http://{}:{}'.format(alltd[0].string, alltd[1].string))
        self.save_to_db(ip_list)
        # return ip_list


class KuaidailiSpider(metaclass=SpiderMeta):
    start_url = 'http://www.kuaidaili.com/free/inha/{}/'

    def getip(self, page_num=3):
        # print('crawling kuaidaili')
        urls = [self.start_url.format(i)
                for i in range(1, page_num+1)]
        ip_list = []
        for url in urls:
            time.sleep(1)
            soup = self.get_html(url)
            proxy_list = soup.find('table', {'class': 'table table-bordered table-striped'}).find('tbody')
            for proxy in proxy_list.find_all('tr'):
                alltd = proxy.find_all('td')
                ip_list.append('{}://{}:{}'.format(alltd[3].string.lower(), alltd[0].string, alltd[1].string.lower()))
        # return ip_list
        self.save_to_db(ip_list)


class XiciSpider(metaclass=SpiderMeta):

    def getip(self, page_num=2):
        # print('crawling xicidaili')
        urls = ['http://www.xicidaili.com/nn/{}'.format(i) for i in range(1, page_num+1)]
        urls.extend(['http://www.xicidaili.com/nt/{}'.format(i) for i in range(1, page_num+1)])
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
        self.save_to_db(ip_list)


def main():
    spiders = [cls() for cls in SpiderMeta.spiders]
    with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
        for spider in spiders:
            executor.submit(spider.getip)


if __name__ == '__main__':
    main()
