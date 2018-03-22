import redis
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/redis_logger.log',
                    filemode='a')

from conf import REDIS_HOST, REDIS_PORT, REDIS_DB_NUM

class RedisClient():
    def __init__(self, setname, host=REDIS_HOST, port=REDIS_PORT, dbnum=REDIS_DB_NUM):
        """
        initial connection
        :param key:
        :return:
        """
        self.setname = setname
        self.__conn = redis.Redis(host=host, port=port, db=dbnum)

    def saveOne(self, ip):
        """
        save an ip
        """
        if self.__conn.sadd(self.setname, ip):
            pass
        else:
            logging.error('IP {} save failed.'.format(ip))

    def remove(self, ip):
        """
        remove an ip
        """
        if self.__conn.srem(self.setname, ip):
            pass
        else:
            logging.error('IP {} delete fialed.'.format(ip))

    def get(self):
        """
        get a ip
        """
        return self.getN(1)[0]

    def getN(self, num):
        """
        return n ip
        """
        return list(map(lambda ip: ip.decode('utf-8'), list(self.__conn.srandmember(self.setname, number=num))))

    def getAll(self):
        """
        return all ips
        """
        return list(map(lambda ip: ip.decode('utf-8'), list(self.__conn.smembers(self.setname))))

    @property
    def size(self):
        return self.__conn.scard(self.setname)


def main():
    r = RedisClient(setname='proxies')
    # r.saveOne('lasttest')
    # print(r.getAll())
    # print(r.size)
    # print(r.get())
    # print(r.getN(2))
    # r.remove('lasttest')
    # print(r.getAll())


if __name__ == '__main__':
    main()

