import queue
import threading
import time

from execution import Execution
from settings import STREAM_DOMAIN, API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID
from strategy import TestRandomStrategy
from streaming import StreamingForexPrices


def trade(events, strategy, execution):

    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            pass
        else:
            if event is not None:
                if event.type == 'TICK':
                    strategy.calculate_signals(event)
                elif event.type == 'ORDER':
                    print("Executing order!")
                    execution.execute_order(event)
        time.sleep(heartbeat)


if __name__ == "__main__":
    heartbeat = 0.5  # 0.5秒間隔
    events = queue.Queue()

    # ドル円の1万通貨を取引
    instrument = "USD_JPY"
    units = 10000

    # OANDAの為替価格ストリーミングを取得
    # アカウント情報などをsetting.pyからインポートしてます
    prices = StreamingForexPrices(STREAM_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID,
                                  instrument, events)

    # 価格ストリーミングの実行。execution.pyから読み込み
    execution = Execution(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)

    # strategy.pyから今回の取引ルールの読み込み
    # 5ティックごとにランダムで決めてます
    strategy = TestRandomStrategy(instrument, units, events)

    # スレッドベースの並列処理で取引処理と価格ストリーミング処理を作成
    trade_thread = threading.Thread(
        target=trade, args=(events, strategy, execution))
    price_thread = threading.Thread(target=prices.stream_to_queue, args=[])

    # 両方のスレッドを開始！
    trade_thread.start()
    price_thread.start()