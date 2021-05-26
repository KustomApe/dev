# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys
from abc import ABCMeta, abstractmethod
import csv

CK = 'gSa8IxJ1MbIzDOdBuQnD8TID8'  # Consumer Key
CS = 'MZnoEmT9STl5d85GAfkRwSNmErC8j9XG5fY026AqQnW3IVdUYM'  # Consumer Secret
AT = '87425177-LSy9F09UKbG5eCItwiBg7HM3B6AcEuutvqSNqcdrO'  # Access Token
AS = 'b6lkdCzyPOARacOBWblP0BSe9Hw33Zh4Fj10eVKQReLJr'  # Accesss Token Secert

class TwitterBot(object):