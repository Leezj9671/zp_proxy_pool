import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/crawl_logger.log',
                    filemode='a')

from time import sleep

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}


class GetProxy():
    def __init__(self):
        pass

    @staticmethod
    def xici(pages=1):
        urls = ['http://www.xicidaili.com/nn/{}',
                'http://www.xicidaili.com/nt/{}']

        for u in urls:
            for page in range(1, pages+1):
                url = u.format(page)
                html = requests.get(url, headers=headers)
                soup = BeautifulSoup(html.text, 'lxml')
                try:
                    alltr = soup.find(id="ip_list").findAll('tr')
                except:
                    logging.error('Can not get table: {}'.format(url))
                    continue
                for tr in alltr[1:]:
                    alltd = tr.findAll('td')
                    yield '{}://{}:{}'.format(alltd[5].string.lower(), alltd[1].string, alltd[2].string)


def main():
    test = GetProxy()
    for i in test.xici():
        print(i)


if __name__ == '__main__':
    main()
