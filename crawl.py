from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 크롤링에 필요한 xpath 주소들
idXpath = '//*[@id="login_user_id"]'
pwXpath = '//*[@id="login_user_password"]'
loginXpath = '//*[@id="form1"]/div[4]'
todoXpath = '//*[@id="dashboard-planner"]/div/div[*]/div'
optionsXpath = '//*[@id="DashboardOptionsMenu_Container"]'
setXpath = '/html/body/span/span/span/span[2]/ul/li[1]/span/ul/li[2]/span'

chatXpath = '//*[@id="inquery"]'
sendXpath = '//*[@id="img_btn"]'
toType = ('조식', '중식', '석식')
menuXpath = '//*[@id="root"]/div/div/div[2]/div/div/div[*]'

# 오늘까지 제출해야하는 과제물 크롤링
def getDashboard(ID, PW):
    # 웹드라이버 선언
    options = webdriver.ChromeOptions()
    options.add_argument("headless") # headless 옵션을 붙여 크롬 창이 백그라운드에서 동작
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10) # 로딩될때까지 기다려주는 시간 10초
    driver.get(url='https://eclass3.cau.ac.kr')

    # 아이디와 비밀번호, 로그인버튼 객체를 찾고 id,pw를 입력한 후 로그인 버튼 클릭
    idBox = driver.find_element(By.XPATH, idXpath)
    pwBox = driver.find_element(By.XPATH, pwXpath)
    loginBtn = driver.find_element(By.XPATH, loginXpath)
    idBox.send_keys(ID)
    pwBox.send_keys(PW)
    loginBtn.click()

    # 로그인 실패시 예외처리
    if driver.current_url == "https://canvas.cau.ac.kr/xn-sso/gw-cb.php":
        return "Fail"

    # 일자별로 정리된 창을 불러오기 위해 설정을 바꾸는 코드. 
    driver.find_element(By.XPATH, optionsXpath).click()
    driver.find_element(By.XPATH, setXpath).click()

    # 오늘까지 TODO인것들을 dashboardTodo에 저장.
    dashBoardTodo = driver.find_elements(By.XPATH, todoXpath)[0].text.split("\n")
    
    retTodo = list()
    # 확인용 print. 실제 gui에는 표시되지 않음.
    print(dashBoardTodo)
    # 없을 경우
    if "Nothing Planned" in dashBoardTodo[0]:
        retTodo.append("Nothing")
    # 있을 경우:과제물 이름 뒤에 붙는 "is not marked as done"을 이용해 과제 이름만 파싱.
    else:
        for i in range(len(dashBoardTodo)):
            if "is not marked as done." in dashBoardTodo[i]:
                retTodo.append(dashBoardTodo[i][3:-23] + "\n")
    
    # todo.puang 에 해야하는 과제물 이름을 씀.
    path = "./resources/todo.puang"
    f = open(path, 'w')
    f.writelines(retTodo)
    f.close()

def getMenu():
    #메뉴 갱신 전까지 임시로 띄울 메시지
    with open("./resources/menu.puang", "w") as f:
        f.write("메뉴 갱신중.. 잠시만 기다려주세요!")

    #크롤링할때 오류 발생시 갱신 실패 메시지를 띄우기 위한 try-except
    try:
        #웹드라이버 선언
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        driver.get(url='https://chat.cau.ac.kr/v2/index.html') # 중앙대 챗봇 링크(로그인 필요 x)
        time.sleep(0.5) # 챗봇 로딩 기다려주는 시간
    
        # 입력, 전송 element 찾기
        chat = driver.find_element(By.XPATH, chatXpath)
        send = driver.find_element(By.XPATH, sendXpath)

        # 조식, 중식, 석식 챗봇에게 물어보기
        for i in range(3):
            time.sleep(0.5) #챗봇 응답 대기 시간
            chat.send_keys(f"서울캠퍼스 {toType[i]} 메뉴")
            send.click()
        time.sleep(1) # 여유 시간

        # 모든 chat 기록 menu에 일단 저장
        menu = list(map(lambda x: x.text, driver.find_elements(By.CLASS_NAME, "bubble_area")))
        
        # 조식, 중식, 석식 메뉴만 파싱하여 menu.puang에 쓰기
        f = open("./resources/menu.puang", "w")
        for i in range(len(menu)):
            if "메뉴입니다." in menu[i]: # "메뉴입니다." <= 필요없는 데이터를 구분짓는 구문
                temp = menu[i].split("\n")
                for j in range(len(temp)):
                    if "메뉴입니다." in temp[j]:
                        temp = temp[j:-1]
                        break
                f.write("\n".join(temp).strip("\n") + "\n\n")
        f.close()
    except:
        with open("./resources/menu.puang", "w") as f:
            f.write("학식 갱신 실패..") # 오류 발생시 갱신 실패 메시지 적기

def getFortune():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    driver.get(url="https://fortune.nate.com/contents/freeunse/freeunseframe.nate?freeUnseId=today04")
    driver.switch_to.frame("contentFrame")

    fortune = list()

    for i in range(1, 24, 2):
        #tee > tbody > tr > td:nth-child(1) > a
        #tee > tbody > tr > td:nth-child(23) > a
        btn = driver.find_element(By.XPATH, f"""//*[@id="tee"]/tbody/tr/td[{i}]""")
        print(btn)
        btn.click()
        time.sleep(0.5)
        context = driver.find_element(By.XPATH, """//*[@id="con_box"]""").text
        fortune.append(context)
    
    for i in range(12):
        with open(f"./resources/fortune/{i}.puang", "w") as f:
            f.write(fortune[i])
if __name__ == "__main__":
    getFortune()
    # getMenu()
    # print(getDashboard(ID, PW))