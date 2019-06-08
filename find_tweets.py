import urllib.request
from requests_oauthlib import OAuth1Session # ライブラリ(1)
from bs4 import BeautifulSoup 
from TwitterAPI import TwitterAPI
import requests
import tweepy
import os

# 各種キーをセット
CONSUMER_KEY = 'PhmPFIDjTcbaxeRmqXqK0KZVR'
CONSUMER_SECRET = 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR'
ACCESS_TOKEN = '87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ'
ACCESS_SECRET = '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7'

#apiを取得
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# twitter内を検索し、結果をエクセルに書き込む
for status in api.search(q='', lang='ja', result_type='recent',count=100): #qに検索語句,countに検索結果の取得数
    status.user.name #useridが出てくる
    status.user.screen_name#ユーザー名が出てくる
    status.text #ツイート内容が出てくる
    status.created_at + datetime.timedelta(hours=9),format #投稿時間が出てくる