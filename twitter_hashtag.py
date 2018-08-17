#!/usr/bin/env python                                                                                                                                             
# -*- coding:utf-8 -*-                                                                                                                                            

from requests_oauthlib import OAuth1Session
import tweepy
import csv
import time
import json

def create_oath_session(oath_key_dict):
    twitter = OAuth1Session(KEYS['consumer_key'],KEYS['consumer_secret'],KEYS['access_token'],KEYS['access_secret'])
    return oath

def tweet_search(search_word, oath_key_dict):
    url = 'https://api.twitter.com/1.1/search/tweets.json?'
    params = {
        'q': unicode(search_word),
        'lang': 'ja',
        'result_type': 'recent',
        'count': '15'
        }
    oath = create_oath_session(oath_key_dict)
    responce = oath.get(url, params = params)
    if responce.status_code != 200:
        return None
    tweets = json.loads(responce.text)
    return tweets

KEYS = {
    'CONSUMER_KEY' : 'PhmPFIDjTcbaxeRmqXqK0KZVR',
    'CONSUMER_SECRET' : 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR',
    'ACCESS_TOKEN' : '87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ',
    'ACCESS_SECRET' : '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7',
}

CONSUMER_KEY = 'PhmPFIDjTcbaxeRmqXqK0KZVR'
CONSUMER_SECRET = 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR'
ACCESS_TOKEN = '87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ'
ACCESS_SECRET = '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7'

#Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

#APIインスタンスを作成
api = tweepy.API(auth)
tweets = tweet_search('#巨乳', oath_key_dict)

tweet_data = []

for tweet in tweepy.Cursor(api.user_timeline, screen_name= 'never_be_a_pm', exclude_replies=True).items():
    if tweets in tweet:
        try:
            tweet_data.append([tweet.id, tweet.created_at, tweet.text.replace('\n', ''), tweets, tweet.favorite_counte, tweet.retweet_count])
            print (tweet_data)
        except Exception as e:
                time.sleep(60 * 15)

### Execute                                                                                                                                                       
with open('today.csv', 'w',newline='',encoding='utf-8') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(["id","created_at","text","fav","RT", "Event name"])
    writer.writerows(tweet_data)
pass