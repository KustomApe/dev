from bs4 import BeautifulSoup
import glob
import requests
import time
import os
import pandas as pd
from tqdm import tqdm
import numpy as np


def get_shopinfo(category, soup):
    shopinfo_th = soup.find('div', {'class': 'shopInfoDetail'}).find_all('th')
    # get 'category' from 'shopinfo_th'
    category_value = list(filter(lambda x: category in x, shopinfo_th))
    if not category_value:
        category_value = None
    else:
        category_value = category_value[0]
        category_index = shopinfo_th.index(category_value)
        shopinfo_td = soup.find('div', {'class': 'shopInfoDetail'}).find_all('td')
        category_value = shopinfo_td[category_index].text.replace('\n', '').replace('\t', '')
    return category_value

# judge [] or in


def judge(category):
    if category is not None:
        category = category.text.replace('\n', '').replace('\t', '')
    else:
        category = np.nan
    return category

# judge [] or in


def judge_atag(category):
    if category is not None:
        category = category.a.text.replace('\n', '').replace('\t', '')
    else:
        category = np.nan
    return category

# judge [] or in


def judge_ptag(category):
    if category is not None:
        category = category.p.text.replace('\n', '').replace('\t', '')
    else:
        category = np.nan
    return category

# judge [] or in


def judge_spantag(category):
    if category is not None:
        category = category.span.text.replace('\n', '').replace('\t', '')
    else:
        category = 0
    return category

# available=1, not=0


def available(strlist):
    available_flg = 0
    if '利用可' in strlist:
        available_flg = 1
    return available_flg

# categorize money


def category2index(category, range):
    if category in range:
        category = range.index(category)
    return category


def scraping(html, df, price_range):
    soup = BeautifulSoup(html, 'html.parser')
    dinner = soup.find('span', {'class': 'shopInfoBudgetDinner'})
    dinner = judge(dinner)
    dinner = category2index(dinner, price_range)
    lunch = soup.find('span', {'class': 'shopInfoBudgetLunch'})
    lunch = judge(lunch)
    lunch = category2index(lunch, price_range)
    genre_tag = soup.find_all('dl', {'class': 'shopInfoInnerSectionBlock cf'})[1]
    genre = genre_tag.find('p', {'class': 'shopInfoInnerItemTitle'})
    genre = judge_atag(genre)
    area_tag = soup.find_all('dl', {'class': 'shopInfoInnerSectionBlock cf'})[2]
    area = area_tag.find('p', {'class': 'shopInfoInnerItemTitle'})
    area = judge_atag(area)
    rating = soup.find('div', {'class': 'ratingInfo'})
    rating = judge_ptag(rating)
    review = soup.find('p', {'class': 'review'})
    review = judge_spantag(review)
    f_meter = soup.find_all('dl', {'class': 'featureMeter cf'})
    # if 'f_meter' is nan, 'size'='customer'='people'='peek'=nan
    if f_meter == []:
        size = np.nan
        customer = np.nan
        people = np.nan
        peek = np.nan
    else:
        meterActive = f_meter[0].find('span', {'class': 'meterActive'})
        size = f_meter[0].find_all('span').index(meterActive)
        meterActive = f_meter[1].find('span', {'class': 'meterActive'})
        customer = f_meter[1].find_all('span').index(meterActive)
        meterActive = f_meter[2].find('span', {'class': 'meterActive'})
        people = f_meter[2].find_all('span').index(meterActive)
        meterActive = f_meter[3].find('span', {'class': 'meterActive'})
        peek = f_meter[3].find_all('span').index(meterActive)
    credits = get_shopinfo('クレジットカード', soup)
    credits = available(credits)
    emoney = get_shopinfo('電子マネー', soup)
    emoney = available(emoney)
    data = [lunch, dinner, genre, area, float(rating), review, size, customer, people, peek, credits, emoney]
    s = pd.Series(data=data, index=df.columns, name=str(i))
    df = df.append(s)
    return df


columns = ['予算(昼)', '予算(夜)', "ジャンル", "エリア", '評価', 'レビュー件数', 'お店サイズ', '客層', '人数/組', 'ピーク時間帯', 'クレジットカード', '電子マネー']
base_url = 'https://www.hotpepper.jp/SA11/'
response = requests.get(base_url).text
soup = BeautifulSoup(response, 'html.parser')
# GET range of price
price_range = soup.find('ul', {'class': 'samaColumnList'}).find_all('a')
price_range = [p.text for p in price_range]
# price_range = ['〜500円', '501〜1000円', '1001〜1500円', '1501〜2000円', '2001〜3000円', '3001〜4000円', '4001〜5000円'
#             , '5001〜7000円', '7001〜10000円', '10001〜15000円', '15001〜20000円', '20001〜30000円', '30001円〜']

num = 16475  # number of data
# num = 1000 # test
df = pd.DataFrame(data=None, columns=columns)

for i in range(num):
    # for i in tqdm(lis):
    html = './html_dir/shop{:0>5}_url.html'.format(i)
    with open(html, "r", encoding='utf-8') as f:
        shop_html = f.read()

    df = scraping(shop_html, df, price_range)
    if i % 1600 == 0:
        percent = i/num*100
        print('{:.3f}% Done'.format(percent))

df.to_csv('shop_info.csv', encoding='shift_jis')
