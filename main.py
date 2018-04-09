import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/proxypool.log',
                    filemode='a')

from concurrent import futures

from proxypool import SpiderMeta
from db import RedisClient
from validIP import CheckIP
from api import app
from conf import REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME
import time


def crawl_ip_process():
    spiders = [cls() for cls in SpiderMeta.spiders]
    start_time_1 = time.clock()
    with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
        for spider in spiders:
            executor.submit(spider.getip, 10)
    print("Crawled IP in {:.4f} seconds".format(time.clock() - start_time_1))
    logging.info("Crawled IP in {:.4f} seconds".format(time.clock() - start_time_1))

def valid_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    fromdb = RedisClient(from_db)
    validdb = RedisClient(to_db)
    from_db_size = fromdb.size
    valid_db_size = validdb.size
    check = CheckIP(from_db=from_db, to_db=to_db)
    check.threads_check_ip()
    print('raw IP counts:{}, valid IP counts before: {}, after: {}\n'.format(from_db_size, valid_db_size, validdb.size))
    logging.info('raw IP counts:{}, valid IP counts before: {}, after: {}\n'.format(from_db_size, valid_db_size, validdb.size))


if __name__ == '__main__':
    # app.run(debug=True)
    # with ProcessPoolExecutor(max_workers=3) as executor:
    #     executor.submit(crawl_ip_process)
    #     executor.submit(valid_ip_process)
    #     executor.submit(valid_ip_process, from_db=REDIS_VALID_SET_NAME)
    # crawl_ip_process()
    while True:
        valid_ip_process()
        valid_ip_process(from_db=REDIS_VALID_SET_NAME)
        time.sleep(10)