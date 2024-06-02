import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

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


def getDashboard(ID, PW):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get(url='https://eclass3.cau.ac.kr')

    idBox = driver.find_element(By.XPATH, idXpath)
    pwBox = driver.find_element(By.XPATH, pwXpath)
    loginBtn = driver.find_element(By.XPATH, loginXpath)
    idBox.send_keys(ID)
    pwBox.send_keys(PW)
    loginBtn.click()

    if driver.current_url == "https://canvas.cau.ac.kr/xn-sso/gw-cb.php":
        return "Fail"

    driver.find_element(By.XPATH, optionsXpath).click()
    driver.find_element(By.XPATH, setXpath).click()
    # driver.get(url='https://eclass3.cau.ac.kr')

    dashBoardTodo = driver.find_elements(By.XPATH, todoXpath)[0].text.split("\n")
    
    retTodo = list()
    print(dashBoardTodo)
    if "Nothing Planned" in dashBoardTodo[0]:
        retTodo.append("Nothing")
    else:
        for i in range(len(dashBoardTodo)):
            if "is not marked as done." in dashBoardTodo[i]:
                retTodo.append(dashBoardTodo[i][3:-23] + "\n")
    path = "./resources/todo.puang"
    if os.path.isfile(path):
        os.remove(path)
    f = open(path, 'w')
    f.writelines(retTodo)
    f.close()

def getMenu():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.get(url='https://chat.cau.ac.kr/v2/index.html')
        time.sleep(0.5)
        chat = driver.find_element(By.XPATH, chatXpath)
        send = driver.find_element(By.XPATH, sendXpath)
        menu = list()
        for i in range(3):
            time.sleep(0.5)
            chat.send_keys(f"서울캠퍼스 {toType[i]} 메뉴")
            send.click()
        time.sleep(1)
        menu = list(map(lambda x: x.text, driver.find_elements(By.CLASS_NAME, "bubble_area")))
        # print(*menu, sep="\n===================\n")
        f = open("./resources/menu.puang", "w")
        for i in range(len(menu)):
            if "메뉴입니다." in menu[i]:
                temp = menu[i].split("\n")
                for j in range(len(temp)):
                    if "메뉴입니다." in temp[j]:
                        temp = temp[j:-1]
                        break
                f.write("\n".join(temp) + "\n\n")
        f.close()
        return
    except:
        return "Fail"

# if __name__ == "__main__":
    # getMenu()
    # print(getDashboard(ID, PW))