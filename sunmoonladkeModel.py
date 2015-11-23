# -*- coding: utf-8 -*-
__author__ = 'Isaac'

import random

import sunmoonlake_ui
from sunmoonlake_ui import Ui_MainWindow
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QDate, pyqtSignal, pyqtSlot, QObject, QThread
from PyQt4.QtGui import QMainWindow, QTableWidget, QTableWidgetItem, QProgressBar

# from myGlobal import *
from jobExecuter import *
from CSVFile import *


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class MyBtn(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(MyBtn, self).__init__(parent=parent)
        self.setDisabled(True)
        self.hide()


    def executeSchedule(self):
        self.parent().executeSchedule()

    def addSchedule(self):
        self.parent().addSchedule()

    def deleteItem(self):
        self.parent().deleteItem()

# class CycleIntThread(QtCore.QThread):
#
#     def __init__(self, parent=None):
#         self.blnRun = True
#         super(CycleIntThread, self).__init__(parent)
#
#     def run(self):
#         self.progressValue = 0
#
#         while self.blnRun:
#
#             if self.progressValue >= 100:
#                 self.progressValue = 0
#             self.progressValue += 0.0001
#             self.emit(QtCore.SIGNAL("progressValue"), self.progressValue)
#             # self.sleep(1) #<~~~~無法正常Sleep,故改用Worker方法


class ApplyStageWorker(QtCore.QObject):

    done = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.exiting = True
        self.myparent = parent

    @QtCore.pyqtSlot()
    def start_apply(self):
        print "apply start"
        now = datetime.datetime.now()

        start_time = None
        while True:
            if now > start_time:
                print "現在較大"
                self.executeWork()
                break
            time.sleep(0.1)

        self.done.emit()


class Worker(QtCore.QObject):

    passValue = QtCore.pyqtSignal(float)
    done = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.exiting = True

    @QtCore.pyqtSlot()
    def get_data(self):
        n = random.randrange(100,200)
        self.progressValue = 0
        while not self.exiting and n > 0:
            # print "test"
            if self.progressValue >= 100:
                self.progressValue = 0
            self.progressValue += 5
            self.passValue.emit(self.progressValue)
            time.sleep(0.1)

        self.done.emit()



class MainWindow(QMainWindow, Ui_MainWindow):
    start_apply = QtCore.pyqtSignal()
    get_data = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.printl("Create Window!")
        # self.lineEdit.setText("ag1040014")
        # self.lineEdit_2.setText("ag1040014")

        self.lineEdit.setText("ag1000022")
        self.lineEdit_2.setText("ag1000022")

        self.locNameList = [
            "文武廟前廣場","水社碼頭廣場(動態表演)","水社碼頭廣場鳳凰木旁B(靜態表演)",
            "水社碼頭廣場鳳凰木旁C(靜態表演)","玄光寺碼頭","伊達邵碼頭廣場",
            "車埕火車站前廣場","車埕鐵道文化廣場"
        ]

        self.tableHeaderNames = [u'日期',u'場地',u'場次',u'帳號',u'密碼',u'線程數',u'延遲交錯']

        now = datetime.datetime.now()
        self.btn = MyBtn(self)
        self.dateEdit.setDate(QtCore.QDate(now.year, now.month, now.day))

        self.btn_Run.clicked.connect(self.btn.executeSchedule)
        self.btn_AddSchedule.clicked.connect(self.btn.addSchedule)
        self.btn_DeleteItem.clicked.connect(self.btn.deleteItem)

        self.setDboxLocalItems(self.locNameList)
        self.calendarWidget.clicked[QtCore.QDate].connect(self.calenderChange)
        self.dateEdit.dateChanged.connect(self.dateEditChange)

        self.tableWidget.setColumnCount(len(self.tableHeaderNames))
        self.tableWidget.setHorizontalHeaderLabels(self.tableHeaderNames)

        self.progressBar = QProgressBar(self.statusbar)
        self.progressBar.setAutoFillBackground(True)
        self.progressBar.setTextVisible(False)
        self.statusbar.addWidget(self.progressBar, 1)
        self.progressBar.hide()

        print 'Connecting process'
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.stdoutReady)
        self.process.readyReadStandardError.connect(self.stderrReady)
        self.process.started.connect(lambda: self.applyStart('Started!'))
        self.process.finished.connect(lambda: self.applyFinish('Finished!'))
        self.dateEdit.setMaximumDate(QtCore.QDate(7999, 12, 28))
        self.dateEdit.setMaximumTime(QtCore.QTime(23, 59, 59))
        self.timeEdit.setTime(QtCore.QTime(9, 58, 0))

        self.action_3.triggered.connect(self.aboutMe)

    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, _fromUtf8('是否結束應用程式?'),
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.process.terminate()
            # self.process.kill()
            self.printl("Stop By User !!")
            event.accept()
        else:
            event.ignore()

    def aboutMe(self):
        # print "aboutMe"
        msg = "日月潭-表演場地租借(7日試用版)\n"
        msg += "=================================\n"
        msg += "作者：劉璟宏\n"
        msg += "程式版本日期：2015/11/23\n"
        msg += "試用到期日：" + str(EXPIRED_DATE) + "\n"
        msg += "=================================\n"
        msg += "@艾爾吉特工作坊版權所有\n"
        QtGui.QMessageBox.information(self, "MessageBox", _fromUtf8(msg), QtGui.QMessageBox.Ok)


    def setDboxLocalItems(self, locNameList):
        if locNameList is None:
            raise Exception("MainWindow.setDboxLocalItems: locNameList必須有內容!!")
        for locName in locNameList:
            self.dbox_Local.addItem(_fromUtf8(locName))

    def calenderChange(self, date):
        self.dateEdit.setDate(date)

    def dateEditChange(self, date):
        self.calendarWidget.setSelectedDate(date)

    # def testApply(self):
    #     from jobExecuter import *
    #     account1 = Account("ag1040014", "ag1040014")
    #     stage1 = Stage(u"文武廟前廣場", "2015", "11", "26", "A")
    #     stage2 = Stage(u"文武廟前廣場", "2015", "11", "26", "B")
    #     try:
    #         jobExec = JobExecuter()
    #         jobExec.addJob(account1, stage1, 1, 2, 2)
    #         jobExec.addJob(account1, stage2, 2, 2, 2)
    #         resultList = jobExec.run()
    #         getResultString(resultList)
    #     except Exception, e:
    #         print e.message
    #         raise e
    #     finally:
    #         RunUnit.processClean()

    def printl(self, text):
        self.append(text + "\n")

    def append(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)

    def stdoutReady(self):
        text = str(self.process.readAllStandardOutput())
        print text.strip()
        self.append(_fromUtf8(text))

    def stderrReady(self):
        text = str(self.process.readAllStandardError())
        print text.strip()
        self.append(_fromUtf8(text))

    def startProgress_ByThread(self):
        self.progressBar.show()
        self.blnStopProgress = False
        self.progressValue = 0
        while not self.blnStopProgress:
        # while self.progressValue < 99:
            if self.progressValue >= 100:
                self.progressValue = 0
            self.progressValue += 0.0001
            self.progressBar.setValue(self.progressValue)

        return True

    def startProgress(self):
        self.progressBar.show()

        self.thread = QtCore.QThread(parent=self)
        self.worker = Worker(parent=None)
        self.worker.moveToThread(self.thread)

        self.get_data.connect(self.worker.get_data)
        self.worker.passValue.connect(self.updateProgressValue)
        self.thread.start(QThread.IdlePriority)
        self.worker.exiting = False
        self.get_data.emit()

        # #--------------------------------------------
        # self.cycleIntThread = CycleIntThread()
        # self.cycleIntThread.start()
        # self.progressBar.show()
        # self.connect(self.cycleIntThread, QtCore.SIGNAL("progressValue"), self.updateProgressValue)
        #
        # #--------------------------------------------

    def stopProgress(self):
        self.progressBar.hide()
        self.worker.exiting = True
        self.btn_Run.setEnabled(True)
        self.btn_AddSchedule.setEnabled(True)
        self.btn_DeleteItem.setEnabled(True)

        # self.blnStopProgress = True
        # self.cycleIntThread.blnRun = False
        # self.progressBar.hide()
        # self.cycleIntThread.terminate()

    def updateProgressValue(self, val):
        # print "updateProgressValue"
        self.progressBar.setValue(val)

    def applyStart(self,msg):
        print msg
        self.startProgress()

    def applyFinish(self,msg):
        print msg
        self.stopProgress()

    def executeSchedule(self):
        self.printl("click start!! self.tableWidget.rowCount() = " + str(self.tableWidget.rowCount()))
        if self.tableWidget.rowCount() < 1:
            return

        h = self.timeEdit.time().hour()
        m = self.timeEdit.time().minute()
        s = self.timeEdit.time().second()
        expected_execute_time = str(h) + ":" + str(m) + ":" + str(s)

        show_web_mode = 0
        if self.checkBox.isChecked():
            # RunUnit.IS_SHOW_WEB = True
            show_web_mode = 1

        self.btn_Run.setEnabled(False)
        self.btn_AddSchedule.setEnabled(False)
        self.btn_DeleteItem.setEnabled(False)

        tempf = tempfile.NamedTemporaryFile(delete=False)
        # print tempf.name

        csv = CSVFile(tempf.name)

        list2D = []
        for i in range(0, self.tableWidget.rowCount()):
            rowList = []
            for j in range(0, self.tableWidget.columnCount()):
                rowList.append(unicode(self.tableWidget.item(i,j).text()))
            list2D.append(rowList)

        csv.writeFrom2DList(list2D)


        if os.path.exists("jobExecuter.py"):
            self.printl('Starting process: jobExecuter.py !!')
            self.process.start('python', ['jobExecuter.py', expected_execute_time, tempf.name, str(show_web_mode)])
        else:
            self.printl('Starting process: jobExecuter.exe !!')
            self.process.start('jobExecuter.exe', [expected_execute_time, tempf.name, str(show_web_mode)])



        # #--------------------------------------------
        # self.thread1 = QtCore.QThread(parent=self)
        # self.applyWorker = ApplyStageWorker(parent=self)
        # self.applyWorker.moveToThread(self.thread1)
        # self.start_apply.connect(self.applyWorker.start_apply)
        # self.thread1.start(QThread.IdlePriority)
        # self.applyWorker.done.connect(lambda: self.applyFinish('Finished!'))
        # self.start_apply.emit()
        # #--------------------------------------------
        # self.testApply()
        # #--------------------------------------------


    def addSchedule(self):
        print "click addSchedule!!"
        row_cnt = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_cnt)
        y = self.dateEdit.date().year()
        m = self.dateEdit.date().month()
        d = self.dateEdit.date().day()

        rent_time = "未定義"
        if self.rbtn_Morning.isChecked():
            rent_time = "早上"
        elif self.rbtn_Afternoon.isChecked():
            rent_time = "下午"
        elif self.rbtn_Evening.isChecked():
            rent_time = "晚上"
        else:
            raise Exception("MainWindow.addSchedule(): 租用時間別未定義!!")

        col1 = QTableWidgetItem(str(y) + "/" + str(m) + "/" + str(d))
        col2 = QTableWidgetItem(self.dbox_Local.currentText())
        col3 = QTableWidgetItem(_fromUtf8(rent_time))
        col4 = QTableWidgetItem(_fromUtf8(self.lineEdit.text()))
        col5 = QTableWidgetItem(_fromUtf8(self.lineEdit_2.text()))
        col6 = QTableWidgetItem(self.spinBox.text())
        col7 = QTableWidgetItem(self.doubleSpinBox.text())
        self.tableWidget.setItem(row_cnt, 0, col1)
        self.tableWidget.setItem(row_cnt, 1, col2)
        self.tableWidget.setItem(row_cnt, 2, col3)
        self.tableWidget.setItem(row_cnt, 3, col4)
        self.tableWidget.setItem(row_cnt, 4, col5)
        self.tableWidget.setItem(row_cnt, 5, col6)
        self.tableWidget.setItem(row_cnt, 6, col7)
        self.tableWidget.resizeColumnsToContents()

        thread_cnt = 0
        for i in range(0, self.tableWidget.rowCount()):
            thread_cnt += int(self.tableWidget.item(i, 5).text())

        self.label_9.setText(str(thread_cnt))

    def deleteItem(self):
        print "click deleteItem!!"
        for item in self.tableWidget.selectedItems():
            # print item.row()
            self.tableWidget.removeRow(item.row())

        self.tableWidget.resizeColumnsToContents()

def main():
    import sys
    app = sunmoonlake_ui.QtGui.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())

def variable():
    print "exect"
    pass

if __name__ == "__main__":
    # processing.freeze_support()
    main()