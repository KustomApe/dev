from selenium import webdriver
import pandas as pd
import time

"""***************************************
初期設定
***************************************"""
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--lang=ja')
browser = webdriver.Chrome(chrome_options=options,
                           executable_path='./cd_v100/chromedriver')
df = pd.DataFrame(columns=['name', 'image', 'price', 'category', 'car'])
url = "https://motorz-garage.com/parts/"

"""******************************
CSS SELECTORの設定
******************************"""
PAGER_NEXT = "li.select-page.arrow a[rel='next']"
POSTS = ".product-item-list__item"
PRODUCT_NAME = ".product-item-list__item-name"
IMAGE = ".product-item-list__item-image img"
PRICE = ".product-item-list__item-price"
CATEGORY = ".product-item-list__item-category"
CAR = ".product-item-list__item-car-name"

"""***************************************
実行部分
***************************************"""

browser.get(url)

while True:  # continue until getting the last page
    if len(browser.find_elements_by_css_selector(PAGER_NEXT)) > 0:
        print("Starting to get posts...")
        posts = browser.find_elements_by_css_selector(POSTS)
        print(len(posts))
        for post in posts:
            try:
                name = post.find_element_by_css_selector(PRODUCT_NAME).text
                print(name)
                thumnailURL = post.find_element_by_css_selector(
                    IMAGE).get_attribute("src")
                print(thumnailURL)
                price = post.find_element_by_css_selector(PRICE).text
                print(price)
                category = post.find_element_by_css_selector(CATEGORY).text
                print(category)
                car = post.find_element_by_css_selector(CAR).text
                print(car)
                se = pd.Series([name, thumnailURL, price, category, car],
                               ["name", "image", "price", "category", "car"])
                df = df.append(se, ignore_index=True)
            except Exception as e:
                print(e)
        btn = browser.find_element_by_css_selector(
            PAGER_NEXT).get_attribute('href')
        print("next url:{}".format(btn))
        time.sleep(3)
        browser.get(btn)
        print("Moving to next page......")
    else:
        print("no pager exist anymore")
        break

print("Finished Scraping. Writing CSV.......")
df.to_csv("output.csv")
print("DONE")