import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename='./logs/redis_logger.log',
                    filemode='a')

import redis

from conf import REDIS_HOST, REDIS_PORT, REDIS_DB_NUM, REDIS_RAW_SET_NAME, REDIS_VALID_SET_NAME, REDIS_PASSWORD


class RedisClient():
    """
    Redis Client
    default:
    setname=REDIS_RAW_SET_NAME, host=REDIS_HOST, port=REDIS_PORT, dbnum=REDIS_DB_NUM
    """
    def __init__(self, setname=REDIS_RAW_SET_NAME, host=REDIS_HOST, port=REDIS_PORT, dbnum=REDIS_DB_NUM, pwd=REDIS_PASSWORD):
        """
        initial connection
        :param key:
        :return:
        """
        self.setname = setname
        self.__conn = redis.Redis(host=host, port=port, db=dbnum, password=pwd)

    def save(self, ip):
        """
        save an ip or some ip
        """
        try:
            if isinstance(ip, list):
                if ip is None:
                    raise "No ip in list"
                else:
                    self.__conn.sadd(self.setname, *ip)
            elif isinstance(ip, str):
                self.__conn.sadd(self.setname, ip)
            else:
                raise "ip is wrong type"
        except Exception as e:
            logging.error('IP {} save failed: {}'.format(ip, e))

    def remove(self, ip):
        """
        remove an ip or some ip
        """
        try:
            if isinstance(ip, list):
                self.__conn.srem(self.setname, *ip)
            elif isinstance(ip, str):
                self.__conn.srem(self.setname, ip)
            else:
                raise "ip is wrong type"
        except Exception as e:
            logging.error('IP {} remove failed: {}'.format(ip, e))

    def pop(self):
        """
        pop an ip
        """
        return self.__conn.spop(self.setname).decode('utf-8')

    def get(self):
        """
        get a ip
        """
        return self.getN(1)[0]

    def getN(self, num):
        """
        return n ip
        """
        try:
            iplist = list(map(lambda ip: ip.decode('utf-8'), list(self.__conn.srandmember(self.setname, number=num))))
        except:
            iplist = []
        return iplist

    def get_all(self):
        """
        return all ips
        """
        return list(map(lambda ip: ip.decode('utf-8'), list(self.__conn.smembers(self.setname))))

    def delete_all(self):
        """
        delete all ips
        """
        self.__conn.flushall()

    @property
    def size(self):
        """
        return key's size
        """
        return self.__conn.scard(self.setname)


if __name__ == '__main__':
    r = RedisClient(setname=REDIS_RAW_SET_NAME)
    # print(r.getAll())
    lst = [i for i in range(10)]
    print(r.get_all())
    r.save(lst)
    print(r.get_all())
    lst = 'test'
    r.save(lst)
    print(r.get_all())
    lst = [i for i in range(10)]    
    r.remove(lst)
    print(r.get_all())
    lst = 'test'
    r.remove(lst)
    print(r.get_all())
    print(r.size)
