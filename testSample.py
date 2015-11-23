import time, random, sys
#from PySide.QtCore import *
#from PySide.QtGui import *

from PyQt4 import QtCore
from PyQt4 import QtGui

# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class ApplicationWindow(QtGui.QMainWindow):
    get_data = QtCore.pyqtSignal()

    def __init__(self, parent = None):

        QtGui.QMainWindow.__init__(self, parent)


        self.thread = QtCore.QThread(parent=self)
        self.worker = Worker(parent=None)
        self.worker.moveToThread(self.thread)

        self.create_main_frame()
        self.create_status_bar()

        self.startButton.clicked.connect(self.start_acquisition) 
        self.stopButton.clicked.connect(self.stop_acquisition)
        self.worker.pixel_list.connect(self.update_figure)
        self.worker.done.connect(self.update_UI)

        self.get_data.connect(self.worker.get_data)


        self.thread.start()


    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()

        self.dpi = 100
        self.width = 10
        self.height = 8
        self.fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        self.axes = self.fig.add_subplot(111)               
        self.axes.axis((0,512,0,120))

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.updateGeometry()    
        self.canvas.draw()
        self.background = None

        self.lE_line, = self.axes.plot(range(512), [0 for i in xrange(512)], animated=True)
        self.hE_line, = self.axes.plot(range(512), [0 for i in xrange(512)], animated=True)          

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.startButton = QtGui.QPushButton(self.tr("&Start"))
        self.stopButton = QtGui.QPushButton(self.tr("&Stop"))

        layout = QtGui.QGridLayout()
        layout.addWidget(self.canvas, 0, 0)
        layout.addWidget(self.mpl_toolbar, 1, 0)
        layout.addWidget(self.startButton, 2, 0)       
        layout.addWidget(self.stopButton, 2, 1)

        self.main_frame.setLayout(layout)
        self.setCentralWidget(self.main_frame)

        self.setWindowTitle(self.tr("XRTdev Interface"))

    def create_status_bar(self):
        self.status_text = QtGui.QLabel("I am a status bar.  I need a status to show!")
        self.statusBar().addWidget(self.status_text, 1)

    def start_acquisition(self):
        self.worker.exiting = False
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.get_data.emit()

    def stop_acquisition(self):
        self.worker.exiting = True
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.cleanup_UI()

    def update_figure(self, lE, hE):
        if self.background == None:
            self.background = self.canvas.copy_from_bbox(self.axes.bbox)
        self.canvas.restore_region(self.background)
        self.lE_line.set_ydata(lE)
        self.hE_line.set_ydata(hE)
        self.axes.draw_artist(self.lE_line)
        self.axes.draw_artist(self.hE_line)
        self.canvas.blit(self.axes.bbox)

    def update_UI(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.cleanup_UI()        

    def cleanup_UI(self):
        self.background = None
        self.axes.clear()        
        self.canvas.draw()

class Worker(QtCore.QObject):

    pixel_list = QtCore.pyqtSignal(list, list)
    done = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.exiting = True

    @QtCore.pyqtSlot()
    def get_data(self):
        # simulate I/O
        print 'data_start'
        n = random.randrange(100,200)
        while not self.exiting and n > 0:
            lE = [random.randrange(5,16) for i in xrange(512)]
            hE = [random.randrange(80,121) for i in xrange(512)]
            self.pixel_list.emit(lE, hE)
            time.sleep(0.05)
            n -= 1
        print 'n: ', n
        self.done.emit()