import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import logging
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler('test_{}.log'.format(strftime("%m%d"))), 
                                            logging.StreamHandler()],
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/proxypool.log',
                    filemode='a')

from proxypool import SpiderMeta
from db import RedisClient
from check_ip import CheckIP
from api import app
from conf import REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME


def crawl_ip_process(timewait=3600):
    while True:
        start_time = time.perf_counter()
        spiders = [cls() for cls in SpiderMeta.spiders]
        with ThreadPoolExecutor(max_workers=len(spiders)) as executor:
            for spider in spiders:
                executor.submit(spider.getip)
        logging.info("Crawl IP Process in {:.4f} seconds".format(time.perf_counter() - start_time))
        time.sleep(timewait)


def raw_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME, timewait=600):
    while True:
        start_time = time.perf_counter()
        raw_db_size = raw_db.size
        if raw_db_size == 0:
            logging.info('Checked raw IP proxy pool. No ip in it now.')
        else:
            valid_db_size = valid_db.size
            check = CheckIP(from_db=from_db, to_db=to_db)
            check.threads_check_ip()
            logging.info('Checked raw IP proxy pool.Raw IP counts:{}, valid IP counts {}->{}, used time: {:.4f} seconds'.format(raw_db_size, valid_db_size, valid_db.size, time.perf_counter() - start_time))
        time.sleep(timewait)


def valid_ip_process(from_db=REDIS_VALID_SET_NAME, to_db=REDIS_VALID_SET_NAME, timewait=20):
    while True:
        valid_db_size = valid_db.size
        if valid_db_size > 0:
            start_time = time.perf_counter()
            check = CheckIP(from_db=from_db, to_db=to_db)
            check.threads_check_ip()
            logging.info('Checked valid proxy pool. Valid IP counts before: {}->{}, used time: {:.4f} seconds'.format(valid_db_size, valid_db.size, time.perf_counter() - start_time))
        time.sleep(timewait)


def api_run():
    app.run(debug=True)


if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=4) as executor:
        # executor.submit(api_run)
        executor.submit(crawl_ip_process)
        executor.submit(raw_ip_process)
        executor.submit(valid_ip_process)
