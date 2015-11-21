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

import subprocess, locale
import unittest, re, time, datetime

def myLog(msg):
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S ') + msg

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

class Python(unittest.TestCase):
    STR_APPLY = ""
    STR_NOT_APPLY = u"該時段已被申請"
    DEFAULT_WAIT_TIMEOUT = 30
    IS_SHOW_WEB = False

    def setUp(self):
        self.base_url = "http://www.sunmoonlake.gov.tw/"
        self.account = Account("ag1040014", "ag1040014")
        self.stage = Stage(u"文武廟前廣場", "2015", "11", "25", "A")

        self.tStart = time.time()#計時開始
        myLog("產生瀏覽器物件")
        if self.IS_SHOW_WEB:
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.PhantomJS('phantomjs')
        self.driver.implicitly_wait(self.DEFAULT_WAIT_TIMEOUT)
        self.verificationErrors = []
        self.accept_next_alert = True

    def processClean(self):
        execCommand("taskkill /F /IM conhost.exe")
        execCommand("taskkill /F /IM phantomjs.exe")

    def login(self, account):
        myLog(u"連線網頁 <"+ self.base_url + "/BuskersLogin.aspx> ...")
        self.driver.get(self.base_url + "/BuskersLogin.aspx")
        myLog("開始登入...")
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").clear()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").send_keys(account.userName)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").clear()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").send_keys(account.passWd)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnLogin").click()
        myLog("登入完成!!")

    def searchApplyCondition(self, stage):
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlSpace")).select_by_visible_text(stage.local)
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlYear")).select_by_visible_text(str(stage.year))
        Select(self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlMonth")).select_by_visible_text(str(stage.month))
        myLog(u"開始查詢場地<" + stage.local + " - " + str(stage.year) + "/" + str(stage.month) + "/" + str(stage.day)+"> ...")
        self.tStart2 = time.time()#計時開始
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()
        myLog("指定場地查詢完成!!")

    def checkApply(self):
        cnt = 1
        while True:
            myLog ("正在檢查開放更新，嚐試次數= " + str(cnt) + " ...")
            eles = self.driver.find_elements_by_xpath("//table[@class='calbox']//span")
            ele_cnt = 1
            for ele in eles:
                #myLog("Search ele_cnt=" + str(ele_cnt))
                if ele.text == self.stage.day:
                    btn_apply = self.waitUntilByParent(ele, By.XPATH, "../input", 0.01)
                    if btn_apply is not None:
                        myLog("日期<" + str(ele.text) + "> 已開放申請!!")
                        btn_apply.click()
                        return
                ele_cnt+=1
            self.tStart2 = time.time()#計時重置
            cnt += 1
            self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()

    def sumbitApply(self, stageTime):
        myLog("發送申請中...")
        self.driver.find_element_by_xpath("//span[@id='ctl00_ContentPlaceHolder1_rdobtnApplyItem']//input[@value='"+stageTime+"']").click()
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ckbxAgree").click()
        #print driver.page_source
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnOk").click()

    def finialCheckResult(self):
        duration1 = self.tEnd - self.tStart
        duration2 = self.tEnd - self.tStart2

        myLog("程式總經歷時間(sec)=" + str(duration1))
        myLog("申請速度(按下查詢->完成申請)=" + str(duration2))

        if self.IS_SHOW_WEB:
            page_content = self.close_alert_and_get_its_text()
        else:
            page_content = self.driver.page_source
        #print page_content
        if page_content.find(self.STR_NOT_APPLY) != -1:
            myLog("該時段已被申請!!")
        else:
            myLog("成功申請!!")

    def test_python(self):
        driver = self.driver
        self.login(self.account)

        #主要業務區
        print "============================================================"
        self.searchApplyCondition(self.stage)
        self.checkApply()
        self.sumbitApply(self.stage.time)
        self.tEnd = time.time()#計時結束
        print "============================================================"

        self.finialCheckResult()

    def old_test_python(self):
        driver = self.driver
        myLog(u"連線網頁 <"+ self.base_url + "/BuskersLogin.aspx> ...")
        driver.get(self.base_url + "/BuskersLogin.aspx")
        myLog("開始登入...")
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").clear()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").send_keys(self.account.userName)
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").clear()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").send_keys(self.account.passWd)
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnLogin").click()
        myLog("登入完成!!")

        Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlSpace")).select_by_visible_text(self.stage.local)
        Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlYear")).select_by_visible_text(str(self.stage.year))
        Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlMonth")).select_by_visible_text(str(self.stage.month))
        myLog(u"開始查詢場地<" + self.stage.local + " - " + str(self.stage.year) + "/" + str(self.stage.month) + "/" + str(self.stage.day)+"> ...")
        tStart2 = time.time()#計時開始
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()
        myLog("指定場地查詢完成!!")
        print "============================================================"

        cnt = 1; blnFind = False
        while True:
            myLog ("正在檢查開放更新，嚐試次數= " + str(cnt) + " ...")
            eles = driver.find_elements_by_xpath("//table[@class='calbox']//span")
            ele_cnt = 1
            for ele in eles:
                #myLog("Search ele_cnt=" + str(ele_cnt))
                if ele.text == self.stage.day:
                    btn_apply = self.find_element_by_parent(ele, By.XPATH, "../input")
                    if btn_apply is not None:
                        blnFind = True
                        myLog("日期<" + str(self.stage.year) + "/" + str(self.stage.month) + "/" + str(ele.text)+"> 已開放申請!!")
                        btn_apply.click()
                        break
                ele_cnt+=1
            if blnFind: break
            tStart2 = time.time()#計時重置
            cnt += 1
            driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()

        myLog("發送申請中...")
        driver.find_element_by_xpath("//span[@id='ctl00_ContentPlaceHolder1_rdobtnApplyItem']//input[@value='"+self.stage.time+"']").click()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_ckbxAgree").click()
        #print driver.page_source
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnOk").click()
        tEnd = time.time()#計時結束
        duration1 = tEnd - self.tStart
        duration2 = tEnd - tStart2

        if self.IS_SHOW_WEB:
            page_content = self.close_alert_and_get_its_text()
        else:
            page_content = self.driver.page_source

        print "============================================================"

        if page_content.find(self.STR_NOT_APPLY) != -1:
            myLog("該時段已被申請!!")
        else:
            myLog("成功申請!!")

        #print page_content
        myLog("程式總經歷時間(sec)=" + str(duration1))
        myLog("申請速度(按下查詢->完成申請)=" + str(duration2))

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
    
    def tearDown(self):
        self.driver.close()
        self.driver.quit()
        self.processClean()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
