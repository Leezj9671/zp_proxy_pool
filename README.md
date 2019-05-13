# ZP_ProxyPool

自己实现的一个简易的代理池，采集多家IP代理

## Technical
- Python 3.6
- Redis

## How to use?
一般使用
```
#开启API
python -m Api.api

#验证IP
python -m Proxy.validIP

#抓取IP
python -m Proxy.proxypool
```

crontab
```
#每五分钟验证一次IP
*/5 * * * * /root/zp_proxy_pool/checkIP.sh /root/zp_proxy_pool > /dev/null 2>&1 &

#固定时间抓取IP
0 8,13,18 * * * /root/zp_proxy_pool/crawl.sh /root/zp_proxy_pool > /dev/null 2>&1 &
```