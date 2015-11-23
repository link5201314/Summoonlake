# -*- coding: utf-8 -*-
__author__ = 'use'
import os, time, logging


DEFAULT_LOG_NAME = "summoonlake"
DEFAULT_LOG_PATH = 'F:\\Selenium IDE\\Sunmoonlake\\summoonlake.log'

logger = logging.getLogger(DEFAULT_LOG_NAME)

def createLogger(log_name, logPath):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(logPath)
    fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - Id=%(thread)d - %(levelname)s - %(message)s')

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)

    # 记录一条日志
    logger.info('Logger Created !!')

def getUUID(kind=0):
    if kind == 0:
        return str(time.time()).replace('.','')
    elif kind == 1:
        return str(int(time.strftime('%Y',time.localtime(time.time())))-1911) + time.strftime('%m%d_%H%M%S',time.localtime(time.time()))
    elif kind == 2:
        return time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
    else:
        return None

try:
    createLogger
except NameError:
    # print("Not in scope!")
    pass
else:
    # print("In scope!")

    dir_path = DEFAULT_LOG_NAME + "_log"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    DEFAULT_LOG_PATH = dir_path + "\\" + getUUID(1) + ".log"

    print "createLog:" + DEFAULT_LOG_PATH
    createLogger(DEFAULT_LOG_NAME, DEFAULT_LOG_PATH)
    print "createLog end!!"
    IS_NEED_LOGGER = False