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
config.read('./config/config.txt')
account_id = config['oanda']['account_id']
api_key = config['oanda']['api_key']

# APIへ接続
oanda = oandapy.API(environment="practice", access_token=api_key)

#過去レートを取得 => granularity:取得したい時間足 (5秒足:'S5', 10秒足:'S10', 1分足:'M1', 15分足:'M15', 1時間足:'H1', 日足:'D' などなど), count:取得件数
res_hist = oanda.get_history(
    instrument="USD_JPY", granularity="H1", count=5000)

#ローソク足情報を取得
res = res_hist.get("candles")

#データフレームに変換しておく
df = pd.DataFrame(res)

#確認
print(df[0:3])
