import sys
import os
from selenium import webdriver
import pandas
import time

"""***************************************
もろもろの設定
***************************************"""
browser = webdriver.Chrome(executable_path='/Users/A-SK/dev/valmont/chromedriver') 
df = pandas.DataFrame()
url = "https://valmont.jp/"

"""******************************
CSS SELECTORの設定
******************************"""

POST = "div#st-container"
LINKS = "li.menu-item"
TARGETS = "a"


"""***************************************
実行部分
***************************************"""

browser.get(url)

while True:
    print("Starting to get posts...")
    links = browser.find_elements_by_css_selector(LINKS)
    print (len(links))
    for link in links:
        try:
            target = link.find_element_by_tag_name(TARGETS).get_attribute("href")
            print(target)
            se = pandas.Series([target], ["target"])
            df = df.append(se, ignore_index=True)
        except Exception as e:
            print(e)
    break

print(df)
print('Finished Scraping and writing output to csv......')

open('output.csv', 'w',)
#6
print("Finished Scraping. Writing CSV.......")
df.to_csv("output.csv")
print("DONE")
