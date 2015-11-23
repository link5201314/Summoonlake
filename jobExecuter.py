# -*- coding: utf-8 -*-
__author__ = 'isaac'

from autoUnit import *
from ThreadPoolRunner import *
from CSVFile import *

EXPIRED_DATE = datetime.datetime(2015,12,2)

class JobExecuter():

    def __init__(self):
        # self.delayMode = delayMode
        # self.delaySec = delaySec
        self.jobList = []

    def getJobCount(self):
        return len(self.jobList)

    def addJob(self, account, stage, threadCount=1, delayMode=1, delaySec=2.0):
        self.jobList.append({'account': account, 'stage': stage, 'threadCount': threadCount, 'delayMode': delayMode, 'delaySec': delaySec})

    def runJob(self, job):
        resultList = []
        threadPool = ThreadPoolRunner()
        try:
            for i in range(0, job.get('threadCount')):
                tempUnit = RunUnit(job.get('account'), job.get('stage'))
                threadPool.addWorker(tempUnit.run, resultList)

            logger.info("JobExecuter.runJob: Ready to run thread, total thread count = " + str(job.get('threadCount')))
            threadPool.runAllWorkerAndWait(delayMode=job.get('delayMode'), delaySec=job.get('delaySec'))
            logger.info('thread complete!!')
            # for result in resultList:
            #     print result[1]
        except Exception, e:
            raise e
        finally:
            threadPool.terminateAll()
        return resultList


    def run(self):
        resultList = []
        threadPool = ThreadPoolRunner()

        try:
            for job in self.jobList:
                threadPool.addWorker(self.runJob, resultList, (job,))

            logger.info("JobExecuter.run(): Ready to run jobs, total job count = " + str(len(self.jobList)))
            threadPool.runAllWorkerAndWait()
            logger.info('JobExecuter complete!!')
            # for result in resultList:
            #     for res in result[1]:
            #         print res[1]
        except Exception, e:
            raise e
        finally:
            threadPool.terminateAll()

        return resultList

def getResultString(resultList):
    jobId = 0 ; s = u"執行結果列印"
    for result in resultList:
        for res in result[1]:
            threadId = res[0]
            account = res[1][0]
            stage = res[1][1]
            res_msg = res[1][2]

            s += "\n*********************************[JobExecuter.showResult(): jobId "+ str(jobId) +"]***************************************\n"
            s += "====================================[Thread " + str(threadId) + " ]=====================================\n"
            s +=  u"使用登入帳密: " + account.userName + " , " + account.passWd + "\n"
            # s += account.userName + " , " + account.passWd + "\n"
            s +=  u"申請場地項目: " + stage.local + "/" + stage.year + "/" + stage.month + "/" + \
                  stage.day + " " + stage.time + "\n"
            s += u"申請結果: " + res_msg + "\n"
            # s +=  "==================================================================================\n"
        jobId += 1

    s += "***********************************************************************************************************\n"
    return s

def main():
    account1 = Account("ag1040014", "ag1040014")
    stage1 = Stage(u"文武廟前廣場", "2015", "11", "26", "A")
    stage2 = Stage(u"文武廟前廣場", "2015", "11", "26", "B")

    try:
        jobExec = JobExecuter()
        jobExec.addJob(account1, stage1, 1, 1, 2)
        jobExec.addJob(account1, stage1, 2, 1, 2)
        # jobExec.addJob(account1, stage2, 5, 1, 2)
        resultList = jobExec.run()

        # jobId = 0
        # for result in resultList:
        #     print "\n***********************************[JobExecuter.showResult(): jobId "+ str(jobId) +"]*****************************************\n"
        #     showResult(result[1])
        #     print "***************************************************************************************************************"
        #     jobId += 1

        # logger.info( getResultString(resultList))
        logger.info(getResultString(resultList))

    except Exception, e:
        print e.message
        raise e
    finally:
        RunUnit.processClean()

def commandLineRun(argv):

    now = datetime.datetime.now()
    logger.info("批次啟動時間    ： " + str(now))
    next_exec_time = argv[1].split(":")
    # print next_exec_time
    h = int(next_exec_time[0])
    m = int(next_exec_time[1])
    s = int(next_exec_time[2])
    # print self.timeEdit.time().hour()
    # print self.timeEdit.time().minute()
    # print self.timeEdit.time().second()

    if int(argv[3]) == 0:
        RunUnit.IS_SHOW_WEB = False
    else:
        RunUnit.IS_SHOW_WEB = True

    start_time = datetime.datetime(now.year, now.month, now.day, hour=h, minute=m, second=s)
    # print start_time

    csv = CSVFile(argv[2], decoding='cp950')
    list2D = csv.readTo2DList()
    if os.path.exists(argv[2]):
        #print('os.path.exists(savePath)')
        os.remove(argv[2])

    # for row in list2D:
    #     for col in row:
    #         print col,
    #     print ""


    if now > start_time:
        # print "現在較大"
        start_time = datetime.datetime(now.year, now.month, now.day, hour=h, minute=m, second=s) + datetime.timedelta(days=1)

    logger.info("等待開始執行時間： " + str(start_time))

    # return

    while True:

        if datetime.datetime.now() >= start_time:
        # if True:
            logger.info("批次開始執行...")
            jobExec = JobExecuter()
            for row in list2D:
                target_dt = row[0].split("/")
                year = target_dt[0]
                month = target_dt[1]
                day = target_dt[2]

                place = row[1]

                rent_time = None
                if row[2] == u"早上":
                    rent_time = "A"
                elif row[2] == u"下午":
                    rent_time = "B"
                elif row[2] == u"晚上":
                    rent_time = "C"

                userName = row[3]
                passWd = row[4]
                thread_cnt = int(row[5])
                delay_sec = float(row[6])

                logger.info(u"加入Job： "+year+"/"+month+"/"+day+" , "+place+" , "+rent_time+" , "+userName+" , "+passWd+" , "+str(thread_cnt)+" , "+str(delay_sec))

                account = Account(userName, passWd)
                stage = Stage(place, year, month, day, rent_time)
                jobExec.addJob(account, stage, thread_cnt, 1, delay_sec)

            resultList = jobExec.run()
            logger.info(getResultString(resultList))

            break

        time.sleep(1)

    logger.info("批次結束執行!!")

if __name__ == "__main__":
    import sys
    if datetime.datetime.now() > EXPIRED_DATE:
        print "抱歉，您的程式試用七天已過期!!"
        sys.exit(0)

    if len(sys.argv) == 1:
        main()
    else:
        logger.info("sys.argv = " +  sys.argv[0] + " , " + sys.argv[1] + " , " + sys.argv[2])
        commandLineRun(sys.argv)



