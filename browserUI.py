from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import requests
import unittest
from dotenv import load_dotenv
from os import getenv
from random import choice
from time import sleep
import json
import re
from random import choice
from random import random as rand
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from io import BytesIO
from hashlib import sha256


class botFactory:
    def __init__(self):
        self.target = "https://www.play.wizard101.com/"
        load_dotenv()
        self.passd = getenv('passBot')

    def makeLogin(self, limit):
        with open("./nameFiles/first",'r',encoding='utf-8') as firstNameFile: firstNames = [i.strip() for i in firstNameFile.read().split()]
        with open("./nameFiles/last",'r',encoding='utf-8') as lastNameFile: lastNames = [i.strip() for i in lastNameFile.read().split()]
        userData = list()
        for i in range(limit):
            username = f'{choice(firstNames)}{choice(lastNames)}{round(rand()*1000)}'
            age = choice(range(6,12))
            if {'username': username, 'age': age} not in userData:
                userData.append({'username': username, 'age': age})
        return userData

    def inputData(self,userData,driver):
        driver.get(self.target)
        wait = WebDriverWait(driver, 10)
        p_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "p-select"))
        )
        p_select.click()
        option = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li[@role='option' and normalize-space()='{userData["age"]}']")
            )
        )
        option.click()
        usernameField = driver.find_element(By.ID, "reg-username")
        passField     = driver.find_element(By.ID, "reg-password").find_element(By.TAG_NAME, "input")
        passFieldConf = driver.find_element(By.ID, "reg-passwordAgain").find_element(By.TAG_NAME, "input")
        usernameField.send_keys(userData["username"])
        passField.send_keys(self.passd)
        passFieldConf.send_keys(self.passd)

    def pipeLine(self,limit):
        inputUserData = self.makeLogin(limit)
        outputUserData = list()
        driver = webdriver.Firefox()
        for user in inputUserData:
            try:
                self.inputData(user,driver)
                outputUserData.append(user)
            except TimeoutError:
                self.inputData(user,driver)
            except Exception as err:
                with open(f'userdata',"a",encoding='utf-8') as jsonfile: json.dump(outputUserData,jsonfile,indent='2')
                print(f'Error: {err}')
            finally:
                input("Press enter once the captcha is complete: ")
                with open(f'cookieFiles/{user["username"]}_cookies.json',"w",encoding='utf-8') as cookieFile: json.dump(driver.get_cookies(),cookieFile,indent=2)
                driver.delete_all_cookies()
            

        driver.quit()
        return outputUserData

class browserUI:
    def __init__(self):
        self.f_opt = FirefoxOptions()
        self.f_opt.add_argument("--headless")
        self.f_opt.add_argument("--window-size=1920,1080")
        load_dotenv()
        self.passd = getenv('passBot')
        with open('userData.json','r',encoding='utf-8') as userFile: self.userData = json.load(userFile)
        self.delim = "Correct|Incorrect"
        self.loginTarget = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    def login(self, target, driver, user):
        driver.get(self.loginTarget)
        u_field = driver.find_element(By.ID, "loginUserName")
        p_field = driver.find_element(By.ID, "loginPassword")
        try:
            l_butt  = driver.find_element(By.CLASS_NAME, "wizardButtonInput")
        except:
            l_butt  = driver.find_element(By.CLASS_NAME, "override")
        u_field.send_keys(user)
        p_field.send_keys(self.passd)
        l_butt.click()
    def firstPassLogic(self,driver,user):
        resp_dict = dict()
        sleep(5)
        try:
            while driver.find_element(By.ID, "nextQuestion"):
                an_el_list = driver.find_elements(By.CLASS_NAME, "answer")
                nextButt = driver.find_element(By.ID, "nextQuestion")
                questionText = self.resolveQuestion(driver)
                randomSelection = choice(an_el_list)
                checkBox = randomSelection.find_element(By.CLASS_NAME, "largecheckbox")
                answerText = randomSelection.find_element(By.CLASS_NAME, "answerText").text
                resp_dict[questionText] = {"resp": answerText, "valid": 0}
                checkBox.click()
                nextButt.click()
                sleep(5)
        except:
            sleep(5)
            driver.find_element(By.CLASS_NAME, "kiaccountsbuttonblue").click()
            #detecting captcha
            try:
                driver.find_element(By.ID, "wrapperWizard101A")
                input("press enter once captcha is complete: ")
                with open(f"./cookieFiles/{user}_cookies.json",'w',encoding='utf-8') as cookieFile: json.dump(driver.get_cookies(),cookieFile,indent=2)
            except:
                print("no captcha detected")
        finally:
            source = driver.page_source
            soup = BeautifulSoup(source, "html.parser")
            answerContainer = soup.find(id="quizResults")
            for div in answerContainer:
                if div.text not in ['\n','QUIZ CORRECT ANSWERS']:
                    try:
                        image_el_src = div.find("img").get("src") ##absolute path is in src
                        headers = {"User-Agent": "Mozilla/5.0"}
                        image_wb = requests.get(image_el_src,headers=headers,timeout=10).content
                        q_el = sha256(image_wb).hexdigest()
                        q_resp = div.text.split(" Answer: ")
                        q_text = q_el
                        q_resp_val = q_resp[1].split()[-1]
                    except:
                        q_el = div.text.split(" Answer: ")
                        q_text = q_el[0][4:].strip()
                        q_resp_val = q_el[1].split()[-1]
                    finally:
                            match q_resp_val:
                                case "Incorrect":
                                    val = 0
                                case "Correct!":
                                    val = 1
                            if resp_dict.get(q_text) != ():
                                resp_dict[q_text]["valid"] = val
        return resp_dict

    def secondPassLogic(self,driver,childList,user):
        resp_dict = dict()
        sleep(5)
        try:
            while driver.find_element(By.ID, "nextQuestion"):
                an_el_list = driver.find_elements(By.CLASS_NAME, "answer")
                nextButt = driver.find_element(By.ID, "nextQuestion")
                questionText = self.resolveQuestion(driver)
                randomSelection = choice(childList.get(questionText))
                for an_el in an_el_list:
                    if an_el.find_element(By.CLASS_NAME, "answerText").text == randomSelection:
                        checkBox = an_el.find_element(By.CLASS_NAME, "largecheckbox")
                resp_dict[questionText] = {"resp": randomSelection, "valid": 0}
                checkBox.click()
                nextButt.click()
                sleep(5)
        except:
            sleep(5)
            driver.find_element(By.CLASS_NAME, "kiaccountsbuttonblue").click()
            #detecting captcha
            try:
                driver.find_element(By.ID, "wrapperWizard101A")
                input("press enter once captcha is complete: ")
                with open(f"./cookieFiles/{user}_cookies.json",'w',encoding='utf-8') as cookieFile: json.dump(driver.get_cookies(),cookieFile,indent=2)
            except:
                print("no captcha detected")
        finally:
            source = driver.page_source
            soup = BeautifulSoup(source, "html.parser")
            answerContainer = soup.find(id="quizResults")
            for div in answerContainer:
                if div.text not in ['\n','QUIZ CORRECT ANSWERS']:
                    try:
                        image_el_src = div.find("img").get("src") ##absolute path is in src
                        headers = {"User-Agent": "Mozilla/5.0"}
                        image_wb = requests.get(image_el_src,headers=headers,timeout=10).content
                        q_el = sha256(image_wb).hexdigest()
                        q_resp = div.text.split(" Answer: ")
                        q_text = q_el
                        q_resp_val = q_resp[1].split()[-1]
                    except:
                        q_el = div.text.split(" Answer: ")
                        q_text = q_el[0][4:].strip()
                        q_resp_val = q_el[1].split()[-1]
                    finally:
                            match q_resp_val:
                                case "Incorrect":
                                    val = 0
                                case "Correct!":
                                    val = 1
                            if resp_dict.get(q_text) != ():
                                resp_dict[q_text]["valid"] = val
        return resp_dict
    def resolveQuestion(self,driver):
        try: ##converted from webcrawler for consistancy
            container = driver.find_element(By.CLASS_NAME, "darkerparchment_content")
            image_el_src = container.find_element(By.TAG_NAME, "img").get_attribute("src") ##absolute path is in src
            headers = {"User-Agent": "Mozilla/5.0"}
            image_wb = requests.get(image_el_src,headers=headers,timeout=10).content
            q_el = sha256(image_wb).hexdigest()
        except:
            q_el = driver.find_element(By.CLASS_NAME, "quizQuestion").text
        return q_el

    def take_quiz(self,target,driver,attempt,parentList,user):
        driver.get(target)
        childList = parentList.copy()
        match attempt:
            case 0:
                try :
                    resp_dict = self.firstPassLogic(driver,user)
                    for key in resp_dict:
                        if resp_dict[key]["valid"] == 0:
                            childList[key].remove(resp_dict[key]["resp"])
                        elif resp_dict[key]["valid"] == 1:
                            childList[key] = [resp_dict[key]["resp"]]
                        else:
                            raise KeyError
                except Exception as err:
                    return 0
            case attempt if attempt > 0:
                try:
                    resp_dict = self.secondPassLogic(driver,childList,user)
                    for key in resp_dict:
                        if resp_dict[key]["valid"] == 0:
                            childList[key].remove(resp_dict[key]["resp"])
                        elif resp_dict[key]["valid"] == 1:
                            childList[key] = [resp_dict[key]["resp"]]
                        else:
                            raise KeyError
                except Exception as err:
                    return 0

        return childList
    def loadCookies(self,driver,user):
        with open(f'./cookieFiles/{user}_cookies.json','r',encoding='utf-8') as cookieFile: cookies = json.load(cookieFile)
        domain = driver.execute_script("return window.location.hostname;")
        for cookie in cookies:
            if "expiry" in cookie: del cookie["expiry"]
            if "sameSite" in cookie: del cookie["sameSite"]
            if cookie['domain'] == str(domain): driver.add_cookie(cookie)

    def getAnswers(self,target,parentData):
        childData = parentData.copy()
        att = 0
        driver = webdriver.Firefox()
        for user in self.userData:
            if not all(len(an_el) == 1 for an_el in childData.values()):
                self.login(target,driver,user['username'])
                self.loadCookies(driver,user['username'])
                driver.refresh()
                results = self.take_quiz(target,driver,att,childData,user['username'])
                driver.delete_all_cookies()
                driver.refresh()
                if results != 0:
                    childData = results.copy()
                    att += 1
            else:
                driver.quit()  
                return childData
        return childData


class test_browserUI(unittest.TestCase):
    #def test_makeLogin(self):
    #    fact = botFactory()
    #    info = fact.makeLogin(1000)
    #def test_inputData(self):
    #    fact = botFactory()
    #    driver = webdriver.Firefox()
    #    userData = {'username': 'MELINDAZHOU587', 'age': 9}
    #    fact.inputData(driver,userData)
    #def test_pipeLine(self):
    #    fact = botFactory()
    #    limit = 1
    #    userdata = fact.pipeLine(limit)
    #    with open("userData.json",'w',encoding='utf=8') as userDataFile: json.dump(userdata,userDataFile,indent=2)
    #def test_login(self):
    #    brow = browserUI()
    #    user = getenv("userNames").split(',')[0]
    #    driver = webdriver.Firefox()
    #    target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    #    brow.login(target,driver,user)
    #    driver.quit()
    #def test_firstPassLogic(self):
    #    brow = browserUI()
    #    user = getenv("userNames").split(',')[0]
    #    driver = webdriver.Firefox()
    #    target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    #    target2 = "https://www.wizard101.com/quiz/trivia/game/animated-film-oscar-winners-trivia"
    #    brow.login(target,driver,user)
    #    driver.get(target2)
    #    brow.firstPassLogic(driver)
    #    driver.quit()
    #def test_secondPassLogic(self):
    #    brow = browserUI()
    #    user = getenv("userNames").split(',')[0]
    #    driver = webdriver.Firefox()
    #    target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    #    target2 = "https://www.wizard101.com/quiz/trivia/game/texas-facts-trivia"
    #    brow.login(target,driver,user)
    #    driver.get(target2)
    #    with open("parentData.json","r") as infile:
    #        data = json.load(infile)
    #    brow.secondPassLogic(driver,data[target2.split('/')[-1]],user)
    #    driver.quit()
    #def test_take_quiz(self):
    #    with open("parentData.json","r") as infile: parentList = json.load(infile)
    #    user = getenv("userNames").split(',')[0]
    #    with open(f"{user}_cookies.json","r") as cookieFile: cookies = json.load(cookieFile)
    #    brow = browserUI()
    #    driver = webdriver.Firefox()
    #    target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    #    brow.login(target,driver,user)
    #    for cookie in cookies:
    #        del cookie["sameSite"]
    #        driver.add_cookie(cookie)
    #    target2 = "https://www.wizard101.com/quiz/trivia/game/horse-trivia"
    #    brow.take_quiz(target2,driver,1,parentList,user)
    #    driver.quit()
    def test_getAnswers(self):
        brow = browserUI()
        target = "https://www.wizard101.com/quiz/trivia/game/dog-breeds-trivia"
        with open("parentData.json","r") as parentFile: childData = json.load(parentFile).copy()[target.split('/')[-1]]
        an = brow.getAnswers(target,childData)
        with open("answerData.json","w",encoding='utf-8') as answerFile: json.dump(an,answerFile,indent=2)

    
        
if __name__=="__main__":
    unittest.main()