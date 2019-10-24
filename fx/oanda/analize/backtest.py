# ライブラリの読み込み
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib

df = pd.read_csv(
    'USDJPY_001001_190609_week.csv',
    index_col='DateTime',
    sep='\s|,',
    engine='python',
    names=[
        'Ticker', 'Per', 'DateTime', 'Time', 'Open', 'High', 'Low', 'Close',
        'Vol'
    ],
    skiprows=1)

# データフレームのインデックスをto_datetimeで変換
df.index = pd.to_datetime(df.index)

# 不要なカラムを落とす
del df['Ticker']
del df['Per']
del df['Time']
del df['Vol']

# Tickから1分間へデータを変更
min_1 = df.resample('T').ohlc()

print(min_1)

# Buyのみ抜き出してdrop_levelでレベルを落とします
buy_1min = min_1.xs('Open', axis=1, drop_level=True)

# 念のため確認してみましょう
# print(buy_1min.head())

# 最初の100行（100分）のみ切り出す
buy_1min_s = buy_1min[0:100]

# 念のたサイズを確認
# print(buy_1min_s.shape)
buy_1min_s.plot()
