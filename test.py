# coding=UTF-8
__author__ = 'use'
import sys
import time
import random
import logging
import tempfile

from CSVFile import *

# while True:
#     print random.randrange(0, 5)

def getUUID(kind=0):
    if kind == 0:
        return str(time.time()).replace('.','')
    elif kind == 1:
        return str(int(time.strftime('%Y',time.localtime(time.time())))-1911) + time.strftime('%m%d_%H%M%S',time.localtime(time.time()))
    elif kind == 2:
        return time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
    else:
        return None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "default"
    else:
        print str(sys.argv)
        print len(sys.argv)
        print sys.argv[2]

    # print tempfile.gettempdir() + "\\" + getUUID(0)
    #
    # # t = tempfile.NamedTemporaryFile(delete=False)
    # # print t.name
    # #
    # # csv = CSVFile(t.name)
    # #
    # # li = []
    # # it1 = [u"一",2,3,4]
    # # it2 = [5,6,7,u"四"]
    # # li.append(it1)
    # # li.append(it2)
    # #
    # # csv.writeFrom2DList(li)
    #
    # path = "c:\\users\\use\\temp\\tmpqjd_8n"
    # csv = CSVFile(path, decoding='cp950')
    #
    # list2D = csv.readTo2DList()
    # for row in list2D:
    #     for col in row:
    #         print col
    # f = open()

    print str('1').zfill(2)

