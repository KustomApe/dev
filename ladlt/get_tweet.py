from requests_oauthlib import OAuth1Session
from requests.exceptions import ConnectionError, ReadTimeout, SSLError
import json, datetime, time, pytz, re, sys, traceback, pymongo
#from pymongo import Connection     # Connection classは廃止されたのでMongoClientに変更
from pymongo import MongoClient
from collections import defaultdict
import numpy as np

KEYS = {  # 自分のアカウントで入手したキーを下記に記載
    'consumer_key': 'PhmPFIDjTcbaxeRmqXqK0KZVR',
    'consumer_secret': 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR',
    'access_token': '87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ',
    'access_secret': '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7',
}

twitter = None
connect = None
db = None
tweetdata = None
meta = None

def initialize():  # twitter接続情報や、mongoDBへの接続処理等initial処理実行
    global twitter, twitter, connect, db, tweetdata, meta
    twitter = OAuth1Session(KEYS['consumer_key'], KEYS['consumer_secret'],
                            KEYS['access_token'], KEYS['access_secret'])
    #   connect = Connection('localhost', 27017)     # Connection classは廃止されたのでMongoClientに変更
    connect = MongoClient('localhost', 27017)
    db = connect.starbucks
    tweetdata = db.tweetdata
    meta = db.metadata

initialize()
