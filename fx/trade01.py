import pandas as pd
import oandapy
import datetime
from datetime import datetime, timedelta
import pytz
# API接続設定のファイルを読み込む
import configparser

# 設定
config = configparser.ConfigParser()
config.read('./config/config.txt')
account_id = config['oanda']['account_id']
api_key = config['oanda']['api_key']

# APIへ接続
oanda = oandapy.API(environment="practice", access_token=api_key)

# ドル円の現在のレートを取得
res = oanda.get_prices(instruments="USD_JPY")

# 中身を確認
print(res)


# 文字列 -> datetime
def iso_to_jp(iso):
    date = None
    try:
        date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ')
        date = pytz.utc.localize(date).astimezone(pytz.timezone("Asia/Tokyo"))
    except ValueError:
        try:
            date = datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%f%z')
            date = date.astimezone(pytz.timezone("Asia/Tokyo"))
        except ValueError:
            pass
    return date


# datetime -> 表示用文字列
def date_to_str(date):
    if date is None:
        return ''
    return date.strftime('%Y/%m/%d %H:%M:%S')


# ドル円の現在のレートを取得
res = oanda.get_prices(instruments="USD_JPY")

print(date_to_str(iso_to_jp(res['prices'][0]['time'])))
