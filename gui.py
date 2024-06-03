import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
import crawl

IDPW_PATH = "./settings/idpw.puang" # id, pw 저장된 주소 미리 선언
todoToday = list() # 비동기 함수를 수월하게 동작시켜주기 위한 오늘까지 해야할 과제물들을 담는 전역변수 미리 선언
dt = QDate()

class Todo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.todayDate = dt.currentDate()
        self.updater = Update(self)
        self.menuUpdater = updateMenu(self)
        self.fortuneUpdater = updateFortune(self)
        self.initUI()
        self.cb = QLabel(self)
        self.cb.setText("Loading...")
        self.cb.move(20, 40)
        self.cb.show()
        self.combo.currentIndexChanged.connect(self.updateFortune)
        self.updater.doneSignal.connect(self.updateCheckbox)
        self.updater.start()
        self.menuUpdater.start()
        self.fortuneUpdater.start()
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateDate)

    def initUI(self):
        self.setWindowTitle('CAU TODO')
        self.setWindowIcon(QIcon('./resources/puang.png'))
        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), './resources/puang.png')
        app.setWindowIcon(QIcon(path))
        
        birthday = ["양력 1월 20일~2월 18일", "양력 2월 19일~3월 20일", "양력 3월 21일~4월 19일", "양력 4월 20일~5월 20일", "양력 5월 21일~6월 21일", "양력 6월 22일~7월 22일", "양력 7월 23일~8월 22일", "양력 8월 23일~9월 23일", "양력 9월 24일~10월 22일", "양력 10월 23일~11월 22일", "양력 11월 23일~12월 24일", "양력 12월 25일~1월 19일"]
        self.combo = QComboBox()
        self.combo.addItems(birthday)
        self.combo.setWindowTitle("생일 입력!")
        self.ftsh = QLabel()
        self.ftsh.setWindowTitle("오늘의 운세")
        self.ftsh.move(20, 20)
        self.ftsh.setText("")
        self.ftsh.show()

        currentTime = QDateTime.currentDateTime()
        self.endDate = QDateEdit()
        self.endDate.setDateTime(currentTime)
        self.endDate.setCalendarPopup(True)

        self.date = QLabel()
        self.updateDate()
        self.statusBar().addWidget(self.date)

        setAction = QAction(QIcon('./resources/cau.png'), 'ID/PW 설정', self)
        setAction.triggered.connect(self.setLogin)
        setAction.setShortcut('Ctrl+W')

        menuAction = QAction(QIcon('./resources/bob.png'), '오늘의 학식', self)
        menuAction.triggered.connect(self.showMenu)

        untilAction = QAction(QIcon('./resources/until.png'), '종강까지 몇일?', self)
        untilAction.triggered.connect(self.setEndDate)

        fortuneAction = QAction(QIcon('./resources/clover.webp'), '오늘의 운세', self)
        fortuneAction.triggered.connect(self.showFortune)

        infoAction = QAction(QIcon('./resources/puang.png'), 'Info', self)

        refreshAction = QAction(QIcon('./resources/refresh.png'), '새로고침', self)
        refreshAction.setShortcut('Ctrl+R')
        refreshAction.triggered.connect(self.updater.start)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        setting = menubar.addMenu('Settings')
        setting.addAction(setAction)

        refresh = menubar.addMenu('Refresh')
        refresh.addAction(refreshAction)

        info = menubar.addMenu('Info')
        info.addAction(menuAction)
        info.addAction(untilAction)
        info.addAction(fortuneAction)
        info.addAction(infoAction)

        self.setGeometry(300, 300, 300, 200)
        self.show()

    def setLogin(self):
        id, ok = QInputDialog.getText(self, 'Set ID', 'Enter eclass ID:')

        if ok:
            pw, ok = QInputDialog.getText(self, 'Set PW', 'Enter eclass PW:', QLineEdit.Password)
        else:
            QMessageBox.warning(self, "FAILED", "다시 설정해주세요!")
            return
        
        if ok:
            QMessageBox.information(self, "OK", "설정 완료!")
        else:
            QMessageBox.warning(self, "FAILED", "다시 설정해주세요!")
            return
        
        if os.path.isfile(IDPW_PATH):
            os.remove(IDPW_PATH)

        f = open(IDPW_PATH, "w")
        f.write(id + "\n" + pw)
        f.close()
        
        self.updater.start()

    def updateDate(self):
        if self.todayDate != dt.currentDate():
            # print(self.todayDate)
            self.updater.start()
            self.menuUpdater.start()
            self.fortuneUpdater.start()

        # print(self.todayDate.daysTo(self.endDate.date()))
        # print(self.endDate.text())
        self.date.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd") + f" 종강까지 D-{self.todayDate.daysTo(self.endDate.date())}")
        self.todayDate = dt.currentDate()

    def updateCheckbox(self):
        global todoToday
        self.cb.clear()
        # print(todoToday)
        self.cb.setText("TODO:\n  " + "  ".join(todoToday))
        self.cb.adjustSize()
        self.cb.move(20, 40)
        self.cb.show()

    def showMenu(self):
        with open('./resources/menu.puang', 'r') as f:
            QMessageBox.information(self, "학식 정보", "".join(f.readlines()).strip())

    def setEndDate(self):
        self.endDate.show()

    def showFortune(self):
        self.combo.show()

    def updateFortune(self):    
        i = self.combo.currentIndex()
        with open(f"./resources/fortune/{i}.puang", "r") as f:
            ft = f.readlines()
        self.ftsh.clear()
        self.ftsh.setText("".join(ft))
        self.ftsh.adjustSize()
        self.ftsh.show()

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
            f = open("./resources/todo.puang", "r")
            todoToday = f.readlines()
            f.close()
            print(todoToday)

        self.doneSignal.emit()

class updateMenu(QThread):
    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        crawl.getMenu()

class updateFortune(QThread):
    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        crawl.getFortune()

# class fortunePopup(QWidget):
#     def __init__(self):
#         QWidget.__init__(self)
#         self.initUI()
#         self.combo.currentIndexChanged.connect(self.updateFortune)

#     def initUI(self):
#         self.setWindowTitle('오늘의 운세!')
#         birthday = ["양력 1월 20일~2월 18일", "양력 2월 19일~3월 20일", "양력 3월 21일~4월 19일", "양력 4월 20일~5월 20일", "양력 5월 21일~6월 21일", "양력 6월 22일~7월 22일", "양력 7월 23일~8월 22일", "양력 8월 23일~9월 23일", "양력 9월 24일~10월 22일", "양력 10월 23일~11월 22일", "양력 11월 23일~12월 24일", "양력 12월 25일~1월 19일"]
#         self.combo = QComboBox()
#         self.combo.addItems(birthday)
#         self.ftsh = QLabel()
#         self.ftsh.move(20, 20)
#         self.ftsh.setText("")
#         self.ftsh.show()
#         self.combo.show()
#         self.setGeometry(300, 300, 300, 200)
#         self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Todo()
    sys.exit(app.exec_())