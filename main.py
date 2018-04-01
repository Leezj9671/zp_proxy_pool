from concurrent import futures

from proxypool import SpiderMeta
from db import RedisClient
from validIP import CheckIP
from api import app
from conf import REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME
import time


def crawl_ip_process():
    spiders = [cls() for cls in SpiderMeta.spiders]
    with futures.ThreadPoolExecutor(max_workers=len(spiders)) as executor:
        for spider in spiders:
            executor.submit(spider.getip)

def valid_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    b = RedisClient(from_db)
    c = RedisClient(to_db)
    print('raw:{}  valid:{}'.format(b.size, c.size))
    check = CheckIP(from_db=from_db, to_db=to_db)
    check.threads_check_ip()
    print('raw:{}  valid:{}\n'.format(b.size, c.size))


if __name__ == '__main__':
    # with ProcessPoolExecutor(max_workers=3) as executor:
    #     executor.submit(crawl_ip_process)
    #     executor.submit(valid_ip_process)
    #     executor.submit(valid_ip_process, from_db=REDIS_VALID_SET_NAME)
    crawl_ip_process()
    valid_ip_process()
    valid_ip_process(from_db=REDIS_VALID_SET_NAME)
    # app.run(debug=True)