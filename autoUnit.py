# -*- coding: utf-8 -*-

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

def execCommand(cmdStr):
    #print("execute")
    p = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retstr = ""
    for line in p.stdout.readlines():
        #print line.decode('cp950'),
        retstr += line.decode(locale.getdefaultlocale()[1])

    retval = p.wait()
    return [retval,retstr]

class RunUnit():
    STR_APPLY = ""
    STR_NOT_APPLY = u"該時段已被申請"
    DEFAULT_WAIT_TIMEOUT = 30

    def ___init(self):
        pass

    def run(self):
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS('phantomjs')
        self.driver.implicitly_wait(self.DEFAULT_WAIT_TIMEOUT)
        self.base_url = "http://www.sunmoonlake.gov.tw/"
        self.verificationErrors = []
        self.accept_next_alert = True

        tStart = time.time()#計時開始
        driver = self.driver
        driver.get(self.base_url + "/BuskersLogin.aspx")
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").clear()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbBuskersCardNo").send_keys("ag1040014")
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").clear()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_tbPassWord").send_keys("ag1040014")
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnLogin").click()
        # Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlSpace")).select_by_visible_text(u"文武廟前廣場")
        # Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlYear")).select_by_visible_text("2015")
        # Select(driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlMonth")).select_by_visible_text("11")
        # driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch").click()

        tStart2 = time.time()#計時開始
        driver.find_element_by_xpath("//span[contains(.,'24')]/../input").click()

        driver.find_element_by_xpath("//span[@id='ctl00_ContentPlaceHolder1_rdobtnApplyItem']//input[@value='A']").click()
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_ckbxAgree").click()
        #print driver.page_source
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnOk").click()
        tEnd = time.time()#計時開始
        duration1 = tEnd -tStart
        duration2 = tEnd - tStart2

        page_content = driver.page_source

        print "============================================================"
        #print page_content
        if page_content.find(self.STR_NOT_APPLY) != -1:
            print "該時段已被申請!!"
        else:
            print "成功申請!!"

        print "duration1=", duration1
        print "duration2=", duration2

        self.driver.close()
        self.driver.quit()
        print execCommand("taskkill /F /IM conhost.exe")

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
        pass
        # self.driver.close()
        # self.driver.quit()
        # print execCommand("taskkill /F /IM conhost.exe")
        # self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    RunUnit().run()
