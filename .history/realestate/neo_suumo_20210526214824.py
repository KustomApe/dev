import selenium import webdriver
import pandas as pd
import time

# settings
options = webdriver.ChromeOptions()
options.add_argument('--headeless')
options.add_argument('--disable-gpu')
options.add_argument('--lang=ja')
