import selenium import webdriver
import pandas as pd
import time

# settings
options = webdriver.ChromeOptions()
options.add_argument('--headeless')
options.add_argument('--disable-gpu')
options.add_argument('--lang=ja')
browser = webdriver.Chrome(chrome_options=options, excecutable_path='./chromedriver')
df = pd.DataFrame(columns=['name', 'address', 'location0', 'location1', 'location2', 'age', 'height', 'floor', 'rent', 'admin', 'others', 'floor_map'])
