# -*- coding: utf-8 -*-
__author__ = 'use'
import os
import subprocess, locale
import re, time, datetime
import tempfile

EXPIRED_DATE = datetime.datetime(2015,12,2)

def getUUID(kind=0):
    if kind == 0:
        return str(time.time()).replace('.','')
    elif kind == 1:
        return str(int(time.strftime('%Y',time.localtime(time.time())))-1911) + time.strftime('%m%d_%H%M%S',time.localtime(time.time()))
    elif kind == 2:
        return time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
    else:
        return None


def execCommand(cmdStr):
    #print("execute")
    p = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retstr = ""
    for line in p.stdout.readlines():
        #print line.decode('cp950'),
        retstr += line.decode(locale.getdefaultlocale()[1])

    retval = p.wait()
    return [retval,retstr]

class Account():
    def __init__(self, user, passwd):
        self.userName = user
        self.passWd = passwd

class Stage():
    def __init__(self, local, year, month, day, time):
        self.local = local
        self.year = year
        self.month = month
        self.day = day
        self.time = time