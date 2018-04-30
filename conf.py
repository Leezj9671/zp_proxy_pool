# Redis的相关配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB_NUM = 0
REDIS_PASSWORD = 'passwd'
REDIS_RAW_SET_NAME = 'raw_proxies'
REDIS_VALID_SET_NAME = 'valid_proxies'

# 检查IP的地址
CHECK_IP_ADD = 'http://111.230.35.79/checkip.php'
CHECK_MAX_WORKERS = 10

# 请求超时时间
REQUESTS_TIMEOUT = 3

# 进程循环时间
CRWAL_PROCESS_TIME = 3600
CHECK_RAW_IP_PROCESS_TIME = 60
CHECK_VALID_IP_PROCESS_TIME = 10