import selenium import webdriver
import pandas as pd
import time

# settings
options = webdriver.ChromeOptions()
options.add_argument('--headeless')
options.add_argument('--disable-gpu')
options.add_argument('--lang=ja')
browser = webdriver.Chrome(chrome_options=options, excecutable_path='./chromedriver')
df = pd.DataFrame(columns=['name', 'address', 'location0', 'location1', 'location2', 'age', 'height', 'floor', 'fee', 'admin', 'others', 'floor_map', 'area'])
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sc=14101&sc=14107&sc=14108&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1'

# CSS selector settings
PAGER_NEXT = 'p.pagination-parts a'
OBJECTS = 'tr.js-cassette_link'
NAME = ''
ADDRESS = ''
LOC0 = ''
LOC1 = ''
LOC2 = ''
AGE = ''
HEIGHT = ''
FLOOR = ''
FEE = ''
ADMIN = ''
OTHERS = ''
FLOOR_MAP = ''
AREA = ''

# Activate Code
browser.get(url)

while True:
    if len(browser.find_elements_by_css_selector(PAGER_NEXT)) > 0:
        print('Start to crawl.')