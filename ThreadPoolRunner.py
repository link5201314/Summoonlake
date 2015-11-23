# coding=UTF-8
__author__ = 'Isaac'

import time
import ctypes
import random
import threading
from threading import Thread

def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class ThreadPoolRunner():

    def __init__(self):
        self.lock = threading.Lock()
        self.threadList = []
        self.runningList = []
        pass

    def addWorker(self, func, resultList, args=(), lockMode=False):
        t = threading.Thread(target=self.threadRunner, args=(len(self.threadList), lockMode,func, resultList, args))
        self.threadList.append(t)
        pass

    def threadRunner(self, id, lockMode, func, resultList, args=()):
        result = None
        try:
            if lockMode: self.lock.acquire()
            result = func(*args)
        finally:
            resultList.append([id, result])
            if lockMode: self.lock.release()

    def clearWorkers(self):
        self.waitWorkers()
        self.threadList[:] = []

    def runWorkers(self, tList, delayMode=0, delaySec=10.0):
        for thread in tList:
            self.runningList.append(thread)
            thread.start()

            if (delaySec < 0 or len(tList) == 1): return
            if delayMode == 1:
                time.sleep(delaySec)
            elif delayMode == 2:
                delaySec = random.randrange(1, delaySec+1)
                time.sleep(delaySec)

    def waitWorkers(self):
        for thread in self.runningList:
            thread.join()

        self.runningList[:] = []

    def terminateAll(self):
        for thread in self.runningList:
            try:
                terminate_thread(thread)
            except Exception, e:
                raise e


    def runAllWorkerAndWait(self, max=None, delayMode=0, delaySec=0.0):
        if max is None: max = len(self.threadList)

        for i in xrange(0,len(self.threadList),max):
            tList = self.threadList[i:i+max]

            self.runWorkers(tList, delayMode=delayMode, delaySec=delaySec)
            self.waitWorkers()


