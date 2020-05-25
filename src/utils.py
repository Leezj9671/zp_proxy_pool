import logging
import os
from logging import handlers


def _logging(log_name, log_path='./logs/', log_level=logging.INFO):
    """日志模块"""
    line_format = '%(asctime)s [%(levelname)s] [%(threadName)s] [%(module)s] %(message)s'
    log_format = logging.Formatter(line_format)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 控制台输出
    cmd = logging.StreamHandler()
    cmd.setFormatter(log_format)
    logger.addHandler(cmd)

    # 保存日志到本地，并按时间分割日志
    os.makedirs(log_path, exist_ok=True)
    log_path = log_path + log_name
    handler = handlers.TimedRotatingFileHandler(filename=log_path, when='D', backupCount=10,
                                                encoding='utf-8')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    return logger


log = _logging('proxy_pool.log')
test_log = _logging('test.log')