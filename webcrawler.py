from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import requests
import unittest
from time import sleep
from json import dump
from io import BytesIO
from hashlib import sha256


class webscraper:
    def __init__(self):
        self.f_opt = FirefoxOptions()
        self.f_opt.add_argument("--headless")
        self.f_opt.add_argument("--window-size=1920,1080")
    def getTarget(self,url,driver):
        try: 
            driver.get(url)
            resp = driver.page_source
            driver.delete_all_cookies()
            an_el_resp = dict()
            ## testing for image based question
            if resp != None:
                soup = BeautifulSoup(resp, "html.parser")
                try:
                    container = soup.select_one("table.darkerparchment_content")
                    image_el_src = container.find("img").get("src") ##absolute path is in src
                    headers = {"User-Agent": "Mozilla/5.0"}
                    image_wb = requests.get(image_el_src,headers=headers,timeout=10).content
                    q_el = sha256(image_wb).hexdigest()
                except:
                    q_el = soup.select_one("div.quizQuestion").text.strip()
                finally:
                    an_container = soup.find_all("span", class_="answerText")
                    an_el_resp[q_el] = list()
                    for an_el in an_container:
                        an_txt      = an_el.text.strip()
                        an_el_resp[q_el].append(str(an_txt))
                return an_el_resp
            else:
                resp.raise_for_status()
        #except requests.exceptions.HTTPError as err:
        #    return f"HTTP error occurred: {err}"
        except Exception as err:
            return f"Other error occurred: {err}"
    def getTarget_multi(self,target,limit):
        driver = webdriver.Firefox(options=self.f_opt)
        flag = True
        q = dict()
        count = 0
        while flag:
            q_el = self.getTarget(target,driver)
            test = str(next(iter(q_el.items()))[0])
            if str(next(iter(q_el.items()))[0]) in q:
                count += 1
                print(f"{str(next(iter(q_el.items()))[0])}: redundant {count}/{limit}")
            elif not(str(next(iter(q_el.items()))[0]) in q):
                q.update(q_el)
                count = 0
                print(f"{str(next(iter(q_el.items()))[0])}: new")
            if count == limit:
                flag = False
            else:
                pass
        driver.quit()
        return q
    def scrapeAvailableQuizes(self,target):
        driver = webdriver.Firefox(options=self.f_opt)
        driver.get(target)
        resp = driver.page_source
        driver.quit()
        soup = BeautifulSoup(resp, "html.parser")
        u_cont = soup.select("div.thumb")
        u = list()
        for u_cont_el in u_cont:
            u_el = u_cont_el.find("a").get("href")
            u.append(u_el)
        return u

    def scrape(self,target,limit):
        quiz = self.scrapeAvailableQuizes(target)
        parent = dict()
        for el in quiz:
            id = el.split('/')[-1]
            if parent.get(id, None) == None: parent[id]=dict() 
            child = self.getTarget_multi(el,limit)
            parent[id].update(child)
        return parent


class testScraper(unittest.TestCase):
    #def test_getTarget(self):
    #    self.f_opt = FirefoxOptions()
    #    self.f_opt.add_argument("--headless")
    #    self.f_opt.add_argument("--window-size=1920,1080")
    #    driver = webdriver.Firefox(options=self.f_opt)
    #    target = "https://www.wizard101.com/quiz/trivia/game/animated-film-oscar-winners-trivia"
    #    scraper = webscraper()
    #    an_el = scraper.getTarget(target,driver)
    #    driver.quit()
    #    self.assertEqual(len(an_el),1)
    #    for i in an_el:
    #        self.assertEqual(len(an_el[i]),4)
    #def test_getTarget_multi(self):
    #    scraper = webscraper()
    #    target = "https://www.wizard101.com/quiz/trivia/game/dog-breeds-trivia"
    #    an_el = scraper.getTarget_multi(target,25)
    #    self.assertEqual(len(an_el),15)
    #def test_scrapeAvailableQuizes(self):
    #    scaper = webscraper()
    #    target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
    #    an_el = scaper.scrapeAvailableQuizes(target)
    #    self.assertEqual(len(an_el),34)
    def test_scrape(self):
        scaper = webscraper()
        limit = 100
        target = "https://www.wizard101.com/quiz/trivia/game/fun-trivia"
        an_el = scaper.scrape(target,limit)
        with open("parentData.json", "w", encoding="utf-8") as out:
            dump(an_el, out, indent=2, sort_keys=True)
        print(an_el)


if __name__=="__main__":
    unittest.main()