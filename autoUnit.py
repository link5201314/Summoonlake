# -*- coding: utf-8 -*-
__author__ = 'Isaac'

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.events import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException

from myGlobal import *
from myLogger import *

class RunUnit():
    STR_APPLY = ""
    STR_NOT_APPLY = u"該時段已被申請"
    DEFAULT_WAIT_TIMEOUT = 30
    IS_SHOW_WEB = False

    def __init__(self, account, stage):
        # logger = logging.getLogger(DEFAULT_LOG_NAME)
        self.base_url = "http://www.sunmoonlake.gov.tw/"
        self.account = account
        self.stage = stage

    @classmethod
    def processClean(self):
        execCommand("taskkill /F /IM phantomjs.exe")
        execCommand("taskkill /F /IM conhost.exe")

    def login(self, account):
        logger.info(u"連線網頁 <"+ self.base_url + "/BuskersLogin.aspx> ...")
        self.driver.get(self.base_url + "/BuskersLogin.aspx")
        logger.info("開始登入...")
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").clear()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").send_keys(account.userName)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").clear()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").send_keys(account.passWd)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnLogin").click()
        logger.info("登入完成!!")

    def searchApplyCondition(self, stage):
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlSpace")).select_by_visible_text(stage.local)
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlYear")).select_by_visible_text(str(stage.year))
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlMonth")).select_by_visible_text(str(stage.month))
        logger.info(u"開始查詢場地<" + stage.local + " - " + str(stage.year) + "/" + str(stage.month) + "/" + str(stage.day)+"> ...")
        self.tStart2 = time.time()#計時開始
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()
        logger.info("指定場地查詢完成!!")

    def checkApply(self):
        cnt = 1
        while True:
            logger.info ("正在檢查開放更新，嘗試次數= " + str(cnt) + " ...")
            eles = self.driver.find_elements_by_xpath("//table[@class='calbox']//span")
            ele_cnt = 1
            for ele in eles:
                #logger.info("Search ele_cnt=" + str(ele_cnt))
                # logger.info("self.stage.day.zfill(2):" + self.stage.day.zfill(2))
                if ele.text == self.stage.day.zfill(2):
                    btn_apply = self.find_element_by_parent(ele, By.XPATH, "../input")
                    if btn_apply is not None:
                        logger.info("日期<" + str(ele.text).zfill(2) + "> 已開放申請!!")
                        btn_apply.click()
                        return
                ele_cnt+=1
            self.tStart2 = time.time()#計時重置
            cnt += 1
            self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()

    def sumbitApply(self, stageTime):
        logger.info("發送申請中...場次代號: " + stageTime)
        self.driver.find_element_by_xpath("//span[@id='ctl00_ContentPlaceHolder1_rdobtnApplyItem']//input[@value='"+stageTime+"']").click()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ckbxAgree").click()
        #print driver.page_source
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnOk").click()

    def finialCheckResult(self):
        duration1 = self.tEnd - self.tStart
        duration2 = self.tEnd - self.tStart2

        logger.info("程式總經歷時間(sec)=" + str(duration1))
        logger.info("申請速度(按下查詢->完成申請)=" + str(duration2))
        if self.IS_SHOW_WEB:
            page_content = self.close_alert_and_get_its_text()
        else:
            page_content = self.driver.page_source
        #print page_content
        if page_content.find(self.STR_NOT_APPLY) != -1:
            return [self.account, self.stage, u"該時段已被申請!!"]
        else:
            return [self.account, self.stage, u"成功申請!!"]

    def run(self):
        try:
            self.tStart = time.time()#計時開始
            logger.info("產生瀏覽器物件")
            if self.IS_SHOW_WEB:
                self.driver = webdriver.Firefox()
            else:
                self.driver = webdriver.PhantomJS('phantomjs')
            self.driver.implicitly_wait(self.DEFAULT_WAIT_TIMEOUT)
            self.verificationErrors = []
            self.accept_next_alert = True

            self.login(self.account)

            #主要業務區
            #logger.debug("============================================================")
            self.searchApplyCondition(self.stage)
            self.checkApply()
            self.sumbitApply(self.stage.time)
            self.tEnd = time.time()#計時結束
            #logger.debug("============================================================")

            result = self.finialCheckResult()
            logger.info(result)
            return result
        except Exception, e:
            print e.message
            raise e
        finally:
            # self.driver.close()
            self.driver.quit()

    def waitUntil(self, condition_t, condition_v, waitSec=None):
        if not waitSec:
            waitSec = 20

        self.driver.implicitly_wait(waitSec)
        try:
            return WebDriverWait(self.driver,waitSec).until(EC.presence_of_element_located((condition_t, condition_v)))
        except TimeoutException:
            return None
        finally:
            self.driver.implicitly_wait(self.DEFAULT_WAIT_TIMEOUT)

    def waitUntilByParent(self, parent, condition_t, condition_v, waitSec=None):
        if not waitSec:
            waitSec = 20

        self.driver.implicitly_wait(waitSec)
        try:
            return WebDriverWait(parent,waitSec).until(EC.presence_of_element_located((condition_t, condition_v)))
        except TimeoutException:
            return None
        finally:
            self.driver.implicitly_wait(self.DEFAULT_WAIT_TIMEOUT)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def find_element(self, how, what):
        element = None
        try: element = self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return element
        return element

    def find_element_by_parent(self, parent, how, what):
        element = None
        try: element = parent.find_element(by=how, value=what)
        except NoSuchElementException, e: return element
        return element
    
    def is_alert_present(self):
        try: self.driver.switch_to.alert
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True


if __name__ == "__main__":
    from ThreadPoolRunner import *
    account1 = Account("ag1040014", "ag1040014")
    stage1 = Stage(u"文武廟前廣場", "2015", "11", "26", "A")
    runUnit1 = RunUnit(account1, stage1)
    runUnit2 = RunUnit(account1, stage1)
    runUnit3 = RunUnit(account1, stage1)
    threadPool = ThreadPoolRunner()
    resultList1 = []
    try:
        threadPool.addWorker(runUnit1.run, resultList1)
        threadPool.addWorker(runUnit2.run, resultList1)
        threadPool.addWorker(runUnit3.run, resultList1)
        threadPool.runAllWorkerAndWait(delayMode=1, delaySec=2)
        logger.info('thread complete!!')
        for result in resultList1:
            print result[1]
    except Exception, e:
        print e.message
        raise e
    finally:
        RunUnit.processClean()
