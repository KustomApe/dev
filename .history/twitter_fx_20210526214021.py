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

class TwitterBot(object):
    def __init__(self):
        self.session = ABCMeta