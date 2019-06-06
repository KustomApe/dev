from statistics import mean
import configparser
import pandas as pd
import oandapy
from datetime import datetime
import pytz

config = configparser.ConfigParser()
config.read('./config/config.txt')  # パスの指定が必要です
account_id = config['oanda']['account_id']
api_key = config['oanda']['api_key']

# APIへ接続
oanda = oandapy.API(environment="practice", access_token=api_key)


#指定した本数分、過去チャートを取得する関数を作成する(今回は1時間足を指定する。)
def get_mdata(num):
    apires = oanda.get_history(
        instrument="USD_JPY", granularity="H1", count=num)
    res = apires.get("candles")
    df = pd.DataFrame(res)
    cN = []
    hN = []
    lN = []
    oN = []
    for i in range(len(df)):
        cN.append(
            round(
                float(df['closeBid'][i]) +
                (float(df['closeAsk'][i]) - float(df['closeBid'][i])) / 2, 3))
        hN.append(
            round(
                float(df['highBid'][i]) +
                (float(df['highAsk'][i]) - float(df['highBid'][i])) / 2, 3))
        lN.append(
            round(
                float(df['lowBid'][i]) +
                (float(df['lowAsk'][i]) - float(df['lowBid'][i])) / 2, 3))
        oN.append(
            round(
                float(df['openBid'][i]) +
                (float(df['openAsk'][i]) - float(df['openBid'][i])) / 2, 3))
    df = pd.DataFrame({
        'time': df['time'],
        'open': oN,
        'close': cN,
        'high': hN,
        'low': lN,
        'volume': df['volume']
    })
    return df


#実験的に6時間だけ動かそう
#スタート時間を指定
startminute = datetime.now().minute
starthour = datetime.now().hour
startday = datetime.now().day

nowminute = datetime.now().minute
nowhour = datetime.now().hour
nowday = datetime.now().day

#ポジションを複数持たないようにする仕組み(本当はget_order()関数がありますが、めんどくさいので、こちらの形をとることにします。)
position = 0

#6時間動かすプログラムを作成(今回は分でカウントしているので、6時間だけ動かしたい場合6×60とする)
while ((nowday - startday) * 24 * 60 + (nowhour - starthour) * 60 +
       (nowminute - startminute) < 360):
    #75本分のローソク足を取得
    Mdata = get_mdata(75)

    #現在値はMdataの一番最後のMdata['close']になっている。
    now_price = Mdata['close'][len(Mdata) - 1]

    #長期移動平均線の現在の値を取得
    long_mean = mean(Mdata['close'])

    #もし現在値と長期移動平均線から30pips離れている場合、ポジションを持つ
    if now_price - long_mean >= 0.30 and position == 0:
        ticket = oanda.create_order(
            account_id,
            instrument="USD_JPY",
            units=5000,
            side='sell',
            type='market')
        #関数：create_order()の引数unitsは、注文通貨量のことなので、1000通貨単位で指定してください。
        position = -1  #売りのポジション
    if now_price - long_mean >= -0.30 and position == 0:
        ticket = oanda.create_order(
            account_id,
            instrument="USD_JPY",
            units=5000,
            side='buy',
            type='market')
        position = 1  #買いのポジション

    #何かしらのポジションを持った状態で、現在値が移動平均線に触れた場合
    #または損切りラインに引っかかった場合ポジションを手放す(損切りを15pipsとする)
    if (position == -1 and now_price - long_mean <= 0) or (
            position == -1 and now_price - ticket['price'] >= 0.15):
        oanda.close_position(account_id, "USD_JPY")
        #positionを0に戻す。
        position = 0
    if (position == 1 and now_price - long_mean >= 0) or (
            position == 1 and now_price - ticket['price'] >= -0.15):
        oanda.close_position(account_id, "USD_JPY")
        #positionを0に戻す。
        position = 0

    #現在時刻を取得
    nowminute = datetime.now().minute
    nowhour = datetime.now().hour
    nowday = datetime.now().day