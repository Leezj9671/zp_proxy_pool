# from concurrent.futures import ProcessPoolExecutor

from proxypool import GetProxy
from db import RedisClient
from validIP import CheckIP
from conf import REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME


def crawl_ip_process():
    print('process1')
    proxy = GetProxy()
    rediscli = RedisClient()
    for info in proxy.xici():
        rediscli.save(info)


def valid_ip_process(from_db=REDIS_RAW_SET_NAME, to_db=REDIS_VALID_SET_NAME):
    print('process2')
    b = RedisClient(from_db)
    c = RedisClient(to_db)
    print('raw:{}  valid:{}'.format(b.size, c.size))
    check = CheckIP(from_db=from_db, to_db=to_db)
    check.threads_check_ip()
    print('raw:{}  valid:{}'.format(b.size, c.size))


if __name__ == '__main__':
    # with ProcessPoolExecutor(max_workers=2) as executor:
    #     executor.submit(crawl_ip_process)
    #     executor.submit(valid_ip_process)
    crawl_ip_process()
    valid_ip_process()
    valid_ip_process(from_db=REDIS_VALID_SET_NAME)