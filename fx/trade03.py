# 必要なライブラリの読み込み
import pandas as pd
import oandapy
import datetime
from datetime import datetime, timedelta
import pytz
# API接続設定のファイルを読み込む
import configparser

# 設定
config = configparser.ConfigParser()
config.read('./config/config.txt')  # パスの指定が必要です
account_id = config['oanda']['account_id']
api_key = config['oanda']['api_key']

# APIへ接続
oanda = oandapy.API(environment="practice", access_token=api_key)

for i in range(6):
    if i == 0:
        res_hist = oanda.get_history(
            instrument="USD_JPY", granularity="H1", count=5000)
    else:
        res_hist = oanda.get_history(
            instrument="USD_JPY", granularity="H1", end=endtime, count=5000)
    res = res_hist.get("candles")
    endtime = res[0]['time']
    if i == 0: res1 = res
    else:
        for j in range(len(res1)):
            res.append(res1[j])
        res1 = res
    print('res ok', i + 1, 'and', 'time =', res1[0]['time'])

#データフレームに変換しておく
df = pd.DataFrame(res1)

#取得件数を数えて出力
print(len(df))
