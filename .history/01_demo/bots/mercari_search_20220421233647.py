from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

word = input("検索したいキーワードを入力してください：")
browser = webdriver.Chrome("./cd_v100/chromedriver")
df_main = pd.DataFrame(columns=['在庫有無','タイトル','値段','URL'])
df_graf = pd.DataFrame(columns=['SOLD','PRICE'])
for num in range(1,100):
   res = browser.get("https://www.mercari.com/jp/search/?page="+str(num)+"&keyword="+word)
   item_boxlist = browser.find_elements_by_css_selector(".items-box")
   if len(item_boxlist) ==0:
       break
   for item_box in item_boxlist:
       if len(item_box.find_elements_by_css_selector(".item-sold-out-badge")) > 0:
           sold = "SOLD"
       else:
           sold = "NOT SOLD"
       sub_title = item_box.find_element_by_class_name("items-box-body")
       title = sub_title.find_element_by_tag_name("h3").text
       print(title)
       item_price = item_box.find_element_by_css_selector(".items-box-price")
       price_text = item_price.text
       price_text = re.sub(r",", "", price_text).lstrip("¥")
       price_text_int = int(price_text)
       print(price_text_int)
       url = item_box.find_element_by_tag_name("a").get_attribute("href")
       data  = pd.Series( [ sold,title,price_text,url ], index=df_main.columns )
       grdata = pd.Series( [ sold,price_text ], index=df_graf.columns )
       df_main = df_main.append( data, ignore_index=True )
       df_graf = df_graf.append( grdata, ignore_index=True )
print(df_main)
sns.stripplot(x='SOLD', y='PRICE', data=df_graf)
plt.show()
sns.pairplot(df_graf,hue="SOLD")
plt.show()
df_main.to_csv("pricedata.csv", encoding="utf_8_sig")
print("終了")