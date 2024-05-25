import os
from selenium import webdriver
from selenium.webdriver.common.by import By

idXpath = '//*[@id="login_user_id"]'
pwXpath = '//*[@id="login_user_password"]'
loginXpath = '//*[@id="form1"]/div[4]'
todoXpath = '//*[@id="dashboard-planner"]/div/div[*]/div'

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

    dashBoardTodo = driver.find_elements(By.XPATH, todoXpath)[0].text.split("\n")
    retTodo = list()
    print(dashBoardTodo)
    if "Nothing Planned" in dashBoardTodo[0]:
        retTodo.append("Nothing")
    else:
        for i in range(len(dashBoardTodo)):
            if "is not marked as done." in dashBoardTodo[i]:
                retTodo.append(dashBoardTodo[i][3:-23] + "\n")
    path = "todo.puang"
    if os.path.isfile(path):
        os.remove(path)
    f = open(path, 'w')
    f.writelines(retTodo)
    f.close()

# if __name__ == "__main__":
#     print(getDashboard(ID, PW))