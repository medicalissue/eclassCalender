import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
import crawl

IDPW_PATH = "/settings/idpw.puang" # id, pw 저장된 주소 미리 선언
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
todoToday = list() # 비동기 함수를 수월하게 동작시켜주기 위한 오늘까지 해야할 과제물들을 담는 전역변수 미리 선언
dt = QDate()

class Todo(QMainWindow):
    #gui init
    def __init__(self):
        super().__init__()
        self.todayDate = dt.currentDate() # 오늘의 날짜 QDate객체로 선언

        #비동기 함수들 연결
        self.updater = Update(self)
        self.menuUpdater = updateMenu(self)
        self.fortuneUpdater = updateFortune(self)

        self.initUI() # ui init
        
        self.updater.doneSignal.connect(self.updateCheckbox) # 글씨 업데이트 함수(updateCheckbox) donesignal 연결

        # 앱 실행시 초기 업데이트 시작
        self.updater.start()
        self.menuUpdater.start()
        self.fortuneUpdater.start()

        # 1초마다 실행되는 타이머 설정
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateDate) # 1초마다 실행되는 함수(updateDate) 설정

    # ui init
    def initUI(self):
        # gui의 제목, 아이콘 설정
        self.setWindowTitle('CAU TODO')
        self.setWindowIcon(QIcon('./resources/puang.png'))
        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), './resources/puang.png')
        app.setWindowIcon(QIcon(path))
        
        # todolist를 보여줄 label(self.cb) 를 미리 선언
        self.cb = QLabel(self)
        self.cb.setText("Loading...") # 초기값
        self.cb.move(20, 40)
        self.cb.show()

        # 운세 조회를 위해 생일을 입력받는 콤보박스(self.combo)를 미리 선언
        birthday = ["양력 1월 20일~2월 18일", "양력 2월 19일~3월 20일", "양력 3월 21일~4월 19일", "양력 4월 20일~5월 20일", "양력 5월 21일~6월 21일", "양력 6월 22일~7월 22일", "양력 7월 23일~8월 22일", "양력 8월 23일~9월 23일", "양력 9월 24일~10월 22일", "양력 10월 23일~11월 22일", "양력 11월 23일~12월 24일", "양력 12월 25일~1월 19일"]
        self.combo = QComboBox()
        self.combo.addItems(birthday)
        self.combo.setWindowTitle("생일 입력!")
        self.combo.setGeometry(500, 100, 500, 100)
        self.combo.currentIndexChanged.connect(self.updateFortune) # self.combo의 값이 변화하였을때 그에 맞는 운세를 팝업해주는 함수(self.updateFortune) 연결

        # 오늘의 운세를 표시할 label 선언
        self.ftsh = QLabel()
        self.ftsh.setWindowTitle("오늘의 운세")
        self.ftsh.move(20, 20)
        self.ftsh.setText("")

        # 종강까지 d-day 를 표시하기 위해, 종강일을 나타낼 변수(self.endDate) 를 초기값을 오늘으로 하여 선언
        currentTime = QDateTime.currentDateTime()
        self.endDate = QDateEdit()
        self.endDate.setDateTime(currentTime)
        self.endDate.setCalendarPopup(True)
        self.endDate.setWindowTitle("종강일자 선택!")
        self.endDate.setGeometry(400, 70, 400, 70)

        # 오늘의 날짜를 statusBar(밑쪽 바) 에 나타내기 위해 오늘 날짜를 저장하는 변수(self.date)를 선언
        self.date = QLabel()
        self.updateDate()
        self.statusBar().addWidget(self.date)

        # 메뉴바(위쪽)에 들어갈 것들을 선언:
        setAction = QAction(QIcon('./resources/cau.png'), 'ID/PW 설정', self) # ID/PW 설정
        setAction.triggered.connect(self.setLogin) # 클릭(활성화) 되었을 시에 실행될 로그인 갱신 함수(self.setLogin) 연결
        setAction.setShortcut('Ctrl+W') # 단축키 설정

        menuAction = QAction(QIcon('./resources/bob.png'), '오늘의 학식', self) # 오늘의 학식
        menuAction.triggered.connect(self.showMenu) # 릭(활성화) 되었을 시에 실행될 학식 메뉴를 띄워주는 함수(self.showMenu) 연결

        untilAction = QAction(QIcon('./resources/until.png'), '종강까지 몇일?', self) # 종강까지 일자 계산기
        untilAction.triggered.connect(self.setEndDate) # 종강까지 일자를 선택하고, 계산하는 함수(self.EndDate) 연결

        fortuneAction = QAction(QIcon('./resources/clover.png'), '오늘의 운세', self) # 별자리별 운세 조회기
        fortuneAction.triggered.connect(self.showFortune) # 생일 범위를 입력받고, 운세를 조회할 수 있는 함수(self.showFortune) 연결

        infoAction = QAction(QIcon('./resources/puang.png'), 'Info', self) # 제작자 보여주기
        infoAction.triggered.connect(self.showinfo)

        refreshAction = QAction(QIcon('./resources/refresh.png'), '새로고침', self) # 수동으로 오늘까지 할 과제를 갱신
        refreshAction.triggered.connect(self.updater.start) # 오늘 할 일을 업데이트하고 갱신해주는 함수(self.updater.start() -> Update 객체의 run() 함수) 연결
        refreshAction.setShortcut('Ctrl+R') # 단축키 설정

        # 위의 메뉴들을 연결하기 위한 메뉴바 선언
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        #메뉴바에 Settings, Refresh, Info 의 메뉴들을 연결 및 하위 기능들 add
        setting = menubar.addMenu('Settings')
        setting.addAction(setAction)

        refresh = menubar.addMenu('Refresh')
        refresh.addAction(refreshAction)

        info = menubar.addMenu('Info')
        info.addAction(menuAction)
        info.addAction(untilAction)
        info.addAction(fortuneAction)
        info.addAction(infoAction)

        # gui의 크기를 설정하고, show
        self.setGeometry(300, 300, 500, 300)
        self.show()

    # ID/PW 설정이 눌렸을때 실행될 함수
    def setLogin(self):
        id, ok = QInputDialog.getText(self, 'Set ID', 'Enter eclass ID:') # id를 입력 팝업창으로 받아오기 (ok 변수는 제대로 입력되었는지 여부가 저장됨.)
        # 제대로 입력되었을경우, pw를 차례로 입력받음. else: 경고창을 띄우고 return
        if ok:
            pw, ok = QInputDialog.getText(self, 'Set PW', 'Enter eclass PW:', QLineEdit.Password)
        else:
            QMessageBox.warning(self, "FAILED", "다시 설정해주세요!")
            return
        # pw가 제대로 입력되었을경우, 설정 완료 창을 띄우고 진행. else: 경고창을 띄우고 return
        if ok:
            QMessageBox.information(self, "OK", "설정 완료!")
        else:
            QMessageBox.warning(self, "FAILED", "다시 설정해주세요!")
            return
        
        # return 되지 않았다는 것은, id, pw를 입력하였다는 뜻이므로 그를 파일에 저장.
        f = open(BASE_DIR + IDPW_PATH, "w", encoding="UTF-8")
        f.write(id + "\n" + pw)
        f.close()
        
        # id, pw가 갱신되었으므로 오늘까지 해야할 일(todo)를 갱신시키기 위하여 업데이트하는 함수를 호출
        self.updater.start()

    # 1초마다 실행되는, statusBar의 오늘 날짜, d-day를 관리하는 함수. 또 일자가 바뀌면 오늘의 todo, 학식, 운세를 자동으로 업데이트시킴.
    def updateDate(self):
        if self.todayDate != dt.currentDate(): # 일자가 달라질 경우
            self.updater.start() # todo update
            self.menuUpdater.start() # 학식 update
            self.fortuneUpdater.start() # 오늘의 운세 update

        self.date.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd") + f" 종강까지 D-{self.todayDate.daysTo(self.endDate.date())}") # statusBar(아랫쪽 줄) 에 오늘의 날짜와, d-day 까지의 날짜를 계산한 것을 표시
        self.todayDate = dt.currentDate() # statusBar 날짜 갱신과, 일자가 달라지는지 확인하기 위해 갱신

    # 오늘까지 todo를 전역변수 todoToday를 참고하여 업데이트 해주는 함수
    def updateCheckbox(self):
        global todoToday # todo를 담아두는 전역 변수
        # todoToday 변수의 내용을 todolist를 보여줄 label(self.cb)에 업데이트 해줌.
        self.cb.clear()
        self.cb.setText("TODO:\n  " + "  ".join(todoToday))
        self.cb.adjustSize()
        self.cb.move(20, 40)
        self.cb.show()

    # 오늘자 학식 메뉴를 팝업해서 보여주는 함수
    def showMenu(self):
        # 학식 정보가 저장된 파일 읽고, 띄우기
        with open(BASE_DIR + '/resources/menu.puang', 'r', encoding="UTF-8") as f:
            QMessageBox.information(self, "학식 정보", "".join(f.readlines()).strip())

    # 종강일자 계산을 위해, 종강일을 선택할수 있게 팝업을 띄워주는 함수
    def setEndDate(self):
        # 일자 선택 라벨을 띄워줌
        self.endDate.show()

    # 오늘의 운세 확인을 위해, 생일 일자를 선택할 수 있게 띄워주는 함수
    def showFortune(self):
        self.combo.show()

    # 오늘의 운세를 파일로부터 갱신하는 함수
    def updateFortune(self):    
        i = self.combo.currentIndex() # 생일 입력 팝업(self.combo)로 부터, 사용자의 생일 범위를 읽어옴.
        # 생일에 해당되는 운세 읽어오기
        with open(BASE_DIR + f"/resources/fortune/{i}.puang", "r", encoding="UTF-8") as f:
            ft = f.readlines()
        # 읽어온 운세를 바탕으로, 운세 팝업을 띄우기
        self.ftsh.clear()
        self.ftsh.setText("".join(ft))
        self.ftsh.adjustSize()
        self.ftsh.show()

    def showinfo(self):
        QMessageBox.information(self, '제작자', 'MADE BY\n\n권준상, 류민혁, 박재휘')


# 아래 함수들이 다른 class 로 선언된 이유:
# 선형적으로 함수들을 실행하게 된다면 gui, 갱신, 조회 등의 기능들은 한 행동이 끝날때까지 동시에 사용할 수 없음
# 따라서 시간이 오래 걸리는(크롤링) 갱신 함수들을 비동기 실행이 가능하게 선언하여, 위 같은 문제를 방지

# todo 업데이트(비동기 실행)
class Update(QThread):
    doneSignal = pyqtSignal() # 행동이 끝났음을 알려주는 시그널 선언. 이는 위에서 updateCheckbox 함수와 연결되어 오늘 까지 todo를 가져오면 자동으로 보여주는걸 갱신

    # init
    def __init__(self, parent):
        super().__init__(parent)

    # 실제로 updater에 연결되어 실행될 함수
    def run(self):
        global todoToday # todo가 갱신된 파일로부터 읽어와 저장할 전역 변수

        # id, pw 파일로부터 읽어오기
        f = open(BASE_DIR + IDPW_PATH, "r", encoding="UTF-8")
        id = f.readline().strip()
        pw = f.readline().strip()
        f.close()

        if id == "" or pw == "": # id 혹은 pw가 공백일 경우
            todoToday = ["Login failed!\n", "Please update ID/PW\n"]
        elif crawl.getDashboard(id, pw) == "Fail": # crawl.getDashboard를 호출하여 크롤링 시도, 로그인 실패할 경우
            todoToday = ["Login failed!\n", "Please update ID/PW\n", "or check internet connection."]
        else: # 크롤링 성공시 오늘 할 일을 todo.puang 파일에서 읽어와 전역변수 todoToday에 저장해줌.
            f = open(BASE_DIR + "/resources/todo.puang", "r", encoding="UTF-8")
            todoToday = f.readlines()
            f.close()

        # todoToday 갱신을 완료했으므로, doneSignal을 줌으로서 updateCheckbox 함수를 실행할 수 있도록 함.
        self.doneSignal.emit()

# 학식 업데이트(비동기 실행)
class updateMenu(QThread):
    # init
    def __init__(self, parent):
        super().__init__(parent)
    # crawl.getMenu() 로 학식 메뉴 파일을 갱신
    def run(self):
        crawl.getMenu()

# 오늘의 운세 업데이트(비동기 실행)
class updateFortune(QThread):
    # init
    def __init__(self, parent):
        super().__init__(parent)
    # crawl.getFortune() 으로 별자리별 오늘의 운세를 갱신
    def run(self):
        crawl.getFortune()

# 실제 gui를 호출하는 코드
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Todo()
    sys.exit(app.exec_())