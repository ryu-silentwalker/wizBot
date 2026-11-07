from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import requests
import unittest

class browserUI:
    def __init__(self):
        self.f_opt = FirefoxOptions()
        self.f_opt.add_argument("--headless")
        self.f_opt.add_argument("--window-size=1920,1080")