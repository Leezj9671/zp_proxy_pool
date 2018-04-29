import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/proxypool.log',
                    filemode='a')

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from proxypool import SpiderMeta
from db import RedisClient
from validIP import CheckIP
from api import app
from conf import REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME
import time

raw_db = RedisClient(REDIS_RAW_SET_NAME)
valid_db = RedisClient(REDIS_VALID_SET_NAME)

def crawl_ip_process():
    while True:
        start_time = time.clock()
        spiders = [cls() for cls in SpiderMeta.spiders]
        with ThreadPoolExecutor(max_workers=len(spiders)) as executor:
            for spider in spiders:
                executor.submit(spider.getip)
        print("Crawled IP in {:.4f} seconds".format(time.clock() - start_time))
        logging.info("Crawl IP Process in {:.4f} seconds".format(time.clock() - start_time))
        # time.sleep(3600)

def raw_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    while True:
        start_time = time.clock()
        raw_db_size = raw_db.size
        if raw_db_size == 0:
            logging.info('Checked raw IP proxy pool. No ip in it now.')
        else:
            valid_db_size = valid_db.size
            check = CheckIP(from_db=from_db, to_db=to_db)
            check.threads_check_ip()
            print('Checked raw IP proxy pool.Raw IP counts:{}, valid IP counts before: {}, after: {}, used time: {:.4f} seconds'.format(raw_db_size, valid_db_size, valid_db.size, time.clock() - start_time))
            logging.info('Checked raw IP proxy pool.Raw IP counts:{}, valid IP counts {}->{}, used time: {:.4f} seconds'.format(raw_db_size, valid_db_size, valid_db.size, time.clock() - start_time))
        time.sleep(60)

def valid_ip_process(from_db=REDIS_VALID_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    while True:
        start_time = time.clock()
        valid_db_size = valid_db.size
        check = CheckIP(from_db=from_db, to_db=to_db)
        check.threads_check_ip()
        print('Checked valid proxy pool. Valid IP counts before: {}->{}, used time: {:.4f} seconds'.format(valid_db_size, valid_db.size, time.clock() - start_time))
        logging.info('Checked valid proxy pool. Valid IP counts before: {}->{}, used time: {:.4f} seconds'.format(valid_db_size, valid_db.size, time.clock() - start_time))
        time.sleep(10)

def api_run():
    app.run(debug=False)

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=3) as executor:
        # executor.submit(api_run)
        executor.submit(crawl_ip_process)
        # executor.submit(raw_ip_process)
        # executor.submit(valid_ip_process)
