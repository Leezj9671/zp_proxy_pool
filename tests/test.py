
import time
import redis
import requests
import concurrent.futures
import logging
logging.basicConfig(handlers=[logging.FileHandler('test_{}.log'.format(time.strftime("%m%d"))), 
                    logging.StreamHandler()],
                    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',)

rconn = redis.Redis(host='111.230.35.79',port=9733,db=0,password='JustForTTT666')
RAW_DB_NAME = 'raw'


def check_amzus(proxy):
    proxy = proxy.decode()
    proxies = {'http': 'http://{}'.format(proxy), 'https': 'http://{}'.format(proxy)}
    # proxies = {'http': 'http://{}'.format(proxy), 'https': 'http://{}'.format(proxy)}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7'
    }
    try:
        resp = requests.get('https://www.amazon.com/gp/bestsellers', proxies=proxies, headers=headers, timeout=3)
    except:
        return False
    content = resp.content.decode('utf8')
    # if resp.status_code != 200 or "you're not a robot" in content:
    #     return False
    # else:
    return True

def get_proxy():
    order_id = 'PR211648269104823232'
    u = 'https://proxy.horocn.com/api/v2/proxies?order_id={}&num=10&format=text&line_separator=unix&can_repeat=no'.format(order_id)
    try:
        resp = requests.get(u)
    except:
        return None
    proxies_list = resp.text.split('\n')
    if '不足' in resp.text or '有误' in resp.text:
        return None
    return proxies_list

def check_proxy():
    rconn.smembers(RAW_DB_NAME)
    ok_list = {}

    for proxy in proxies_list:
        proxies = {'https': 'https://{}'.format(proxy)}
        st = time.time()
        try:
            resp = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=3)
            rtime = time.time() - st
            rip = resp.json()['origin'].split(',')[0].strip()
            if proxy.split(':')[0] == rip:
                ok_list[proxy] = rtime
        except:
            pass
    for k, v in enumerate(ok_list):
        if not check_amzus(k):
            ok_list.pop(proxy)
    for k, v in enumerate(ok_list):
        rconn.zadd('test:ok', v, k)

# def check_proxy(proxy):
    
def haip_proxy():

    u = 'http://111.230.35.79:9032/pool/get/amzus'
    proxies_list = requests.get(u).json()['pool']
    print(len(proxies_list))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = {executor.submit(check_amzus, proxy): proxy for proxy in proxies_list}

# haip_proxy()

def get_proxy_process():
    '''站大爷代理'''
    rdb = 'amz_zdy'
    while True:
        rconn.delete(rdb)
        proxies_list = get_proxy_zdy()
        if proxies_list:
            logging.info("Get {} proxies, total: {}".format(len(proxies_list), rconn.scard(rdb)))
            for proxy in proxies_list:
                rconn.sadd(rdb, proxy)
        time.sleep(20)

def check_proxy_process():
    while True:
        if rconn.scard(RAW_DB_NAME) > 0:
            p = rconn.spop(RAW_DB_NAME)
            rconn.sadd('useless', p)
            if check_amzus(p):
                rconn.sadd('amz', p)
            time.sleep(0.5)
        else:
            time.sleep(10)


def check_okproxy_process():
    ori_db = 'amz'
    useless = 'useless'
    while True:
        if rconn.scard(ori_db) > 0:
            p = rconn.spop(ori_db)
            rconn.sadd(useless, p)
            if check_amzus(p):
                rconn.sadd(ori_db, p)
            time.sleep(0.5)
        else:
            time.sleep(15)


def get_proxy_zdy():
    '''站大爷代理获取'''
    u = 'http://www.zdopen.com/ShortS5Proxy/GetIP/?api=201910260925209082&akey=4b1fd688f54ea17b&order=2&type=3'
    try:
        resp = requests.get(u).json()
    except:
        return None
    if resp['code'] == '10001':
        proxies_list = []
        for proxy in resp['data']['proxy_list']:
            proxies_list.append('{}:{}'.format(proxy['ip'], proxy['port']))
        return proxies_list
    else:
        return None


def api():
    from flask import Flask


    app = Flask(__name__)


    @app.route('/getall', methods=['GET'])
    def getAll():
        lst = []
        for i in rconn.smembers('amz_zdy'):
            lst.append(i.decode())
        return '\n'.join(lst)

    @app.route('/getall1', methods=['GET'])
    def getall1():
        lst = []
        for i in rconn.smembers('amz'):
            lst.append(i.decode())
        return '\n'.join(lst)

    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # get_proxy_process()
    # check_proxy_process()
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # executor.submit(get_proxy_process)
        # executor.submit(check_okproxy_process)
        # executor.submit(api)
    # api()
    print(get_proxy_zdy())
