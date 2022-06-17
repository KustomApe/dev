#スクレイピングに必要なモジュール
import requests
from bs4 import BeautifulSoup
import pandas as pd

import time #sleep用
import sys #エラー検知用
import re #正規表現

#レースIDの作成
import itertools

YEAR = ['2020']
CODE = [str(num+1).zfill(2) for num in range(10)]
RACE_COUNT = ['01']
DAYS = ['01']
RACE_NUM = ['01']

race_ids = list(itertools.product(YEAR,CODE,RACE_COUNT,DAYS,RACE_NUM))
SITE_URL = ["https://race.netkeiba.com/race/result.html?race_id={}".format(''.join(race_id)) for race_id in race_ids]

df = pd.DataFrame()

for sitename,race_id in zip(SITE_URL,race_ids):
#時間を空けてアクセスするようにsleepを設定する
    time.sleep(3)
    try:
        #スクレイピング対策のURLにリクエストを送り、HTMLを取得する
        res = requests.get(sitename)
        res.raise_for_status() #URLが正しくない場合、例外を発生させる
        #レスポンスのHTMLからBeautifulsoupオブジェクトを創る

        soup = BeautifulSoup(res.content, 'html.parser')

        #titleタグの文字列を取得する

        title_text = soup.find('title').get_text()

        print(title_text)

        #順位のリスト作成
        Ranks = soup.find_all('div', class_='Rank')
        Ranks_list = []

        for Rank in Ranks:
            Rank = Rank.get_text()
            Ranks_list.append(Rank)

        #馬名取得
        Horse_Names = soup.find_all('span', class_='Horse_Name')
        Horse_Names_list = []
        for Horse_Name in Horse_Names:
            #馬名のみ取得（lstrip()先頭の空白削除、rstrip()改行削除）
            Horse_Name = Horse_Name.get_text().lstrip().rstrip('\n')
            #リスト作成
            Horse_Names_list.append(Horse_Name)
        #人気取得
        Ninkis = soup.find_all('span', class_='OddsPeople')
        Ninkis_list = []
        for Ninki in Ninkis:
            Ninki = Ninki.get_text()
            Ninkis_list.append(Ninki)

        #枠取得

        Wakus = soup.find_all('td', class_=re.compile("Num Waku"))

        Wakus_list = []

        for Waku in Wakus:

        Waku = Waku.get_text().replace('\n','')

        #リスト作成

        Wakus_list.append(Waku)

            #コース、距離取得
            Distance_Course = soup.find_all('span')
            Distance_Course = re.search(r'.[0-9]+m', str(Distance_Course))
            Course = Distance_Course.group()[0]
            Distance = re.sub("\\D", "", Distance_Course.group())
            se = pd.Series([race_id, Ranks_list, Wakus_list, Horse_Names_list, Course, Distance, Ninkis_list],
            ["race_id", "Ranks_list", "Wakus_list", "Horse_Names_list", "Course", "Distance", "Ninkis_list"])

            df = pd.DataFrame({
                'レースID':''.join(race_id),
                '順位':Ranks_list,
                '枠':Wakus_list,
                '馬名':Horse_Names_list,
                'コース':Course,
                '距離':Distance,
                '人気':Ninkis_list,
            })

            #print(df.head())
            #result_df = pd.concat([result_df,df],axis=0)
            df = df.concat([se,df],axis=0)

    except:

print(sys.exc_info())

print("サイト取得エラー")

#print(result_df)

df.to_csv('result.csv')