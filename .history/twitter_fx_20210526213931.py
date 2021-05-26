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

class TwitterBot(object):
    def __init__(self):
        self.session = ABCMeta