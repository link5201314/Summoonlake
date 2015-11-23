__author__ = 'isaac'

IS_NEED_LOGGER = False

if __name__ == "__main__":
    # processing.freeze_support()
    import sys
    import sunmoonladkeModel
    import sunmoonlake_ui


    app = sunmoonlake_ui.QtGui.QApplication(sys.argv)
    window = sunmoonladkeModel.MainWindow()

    window.show()
    sys.exit(app.exec_())