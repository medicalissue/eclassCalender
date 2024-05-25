import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
import crawl
from datetime import datetime

IDPW_PATH = "./settings/idpw.puang"
todoToday = list()

class Todo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todayDate = datetime.now().date()
        self.initUI()
        self.cb = QLabel(self)
        self.cb.show()
        self.updater.doneSignal.connect(self.updateCheckbox)
        self.updater.start()
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateDate)

    def initUI(self):
        self.setWindowTitle('CAU TODO')
        self.setWindowIcon(QIcon('./resources/puang.png'))
        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), './resources/puang.png')
        app.setWindowIcon(QIcon(path))

        self.date = QLabel()
        self.updateDate()
        self.statusBar().addWidget(self.date)

        setAction = QAction(QIcon('./resources/cau.png'), 'Set ID/PW', self)
        setAction.triggered.connect(self.setLogin)
        setAction.setShortcut('Ctrl+W')

        infoAction = QAction(QIcon('./resources/puang.png'), 'Info', self)

        refreshAction = QAction(QIcon('./resources/refresh.png'), 'Refresh', self)
        refreshAction.setShortcut('Ctrl+R')
        self.updater = Update(self)
        refreshAction.triggered.connect(self.updater.start)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        setting = menubar.addMenu('Settings')
        setting.addAction(setAction)

        refresh = menubar.addMenu('Refresh')
        refresh.addAction(refreshAction)

        info = menubar.addMenu('Info')
        info.addAction(infoAction)

        self.setGeometry(300, 300, 300, 200)
        self.show()

    def setLogin(self):
        id, ok = QInputDialog.getText(self, 'Set ID', 'Enter eclass ID:')

        if ok:
            pw, ok = QInputDialog.getText(self, 'Set PW', 'Enter eclass PW:', QLineEdit.Password)
        else:
            QMessageBox.warning(self, "OK", "다시 설정해주세요!")
            return
        
        if ok:
            QMessageBox.information(self, "OK", "설정 완료!")
        else:
            QMessageBox.warning(self, "OK", "다시 설정해주세요!")
            return
        
        if os.path.isfile(IDPW_PATH):
            os.remove(IDPW_PATH)

        f = open(IDPW_PATH, "w")
        f.write(id + "\n" + pw)
        f.close()
        
        self.updater.start()

    def updateDate(self):
        if self.todayDate != datetime.now().date():
            # print(self.todayDate)
            self.updater.start()
        self.date.setText(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        self.todayDate = datetime.now().date()

    def updateCheckbox(self):
        global todoToday
        self.cb.clear()
        # print(todoToday)
        self.cb.setText("TODO:\n  " + "  ".join(todoToday))
        self.cb.adjustSize()
        self.cb.move(20, 40)
        self.cb.show()

class Update(QThread):
    doneSignal = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        global todoToday
        f = open(IDPW_PATH, "r")
        id = f.readline().strip()
        pw = f.readline().strip()
        # print(id, pw)
        f.close()

        if id == "" or pw == "":
            todoToday = ["Login failed!\n", "Please update ID/PW\n"]
        elif crawl.getDashboard(id, pw) == "Fail":
            # print("asdkadiik")
            todoToday = ["Login failed!\n", "Please update ID/PW\n", "or check internet connection."]
        else:
            f = open("todo.puang", "r")
            todoToday = f.readlines()
            f.close()
            print(todoToday)

        self.doneSignal.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Todo()
    sys.exit(app.exec_())