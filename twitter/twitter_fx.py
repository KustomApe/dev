# -*- coding: utf-8 -*-

import config
from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys
from abc import ABCMeta, abstractmethod
import csv

CK = config.CK
CS = config.CS
AT = config.AT
ATS = config.AS
twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

params ={'count' : 5} #取得数
res = twitter.get(url, params=params)

if res.status_code == 200:
    timelines = json.loads(res.text)
    for i in timelines:
        print(i)
else:
    print('Failed: %d' % res.status_code)