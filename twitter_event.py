#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tweepy
import csv
import time
# from config import CONFIG

# 各種ツイッターのキーをセット
# CONSUMER_KEY = CONFIG['PhmPFIDjTcbaxeRmqXqK0KZVR']
# CONSUMER_SECRET = CONFIG['TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR']
# ACCESS_TOKEN = CONFIG['87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ']
# ACCESS_SECRET = CONFIG['6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7']

CONSUMER_KEY = 'PhmPFIDjTcbaxeRmqXqK0KZVR'
CONSUMER_SECRET = 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR'
ACCESS_TOKEN = '87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ'
ACCESS_SECRET = '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7'

#FLASKのキーの設定
# SECRET_KEY = CONFIG["SECRET_KEY"]

#Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
#APIインスタンスを作成
api = tweepy.API(auth)

#ツイート取得
tweet_data = []
event_info = tweet.

for tweet in tweepy.Cursor(api.user_timeline,screen_name = "never_be_a_pm",exclude_replies = True).items():
	if not tweet.retweeted: #RT入れると他人のRT入っちゃうので除外
		try:  	
		    tweet_data.append([tweet.id,tweet.created_at,tweet.text.replace('\n',''),tweet.favorite_count,tweet.retweet_count])
		    print(tweet_data)
		except Exception as e: #rate limit到達するとエラーが起こるのでキャッチする
			time.sleep(60 * 15) # 15分で解決するらしいよ

#csv出力
with open('today.csv', 'w',newline='',encoding='utf-8') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(["id","created_at","text","fav","RT", "Event name"])
    writer.writerows(tweet_data)
pass