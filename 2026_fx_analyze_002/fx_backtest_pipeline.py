#!/usr/bin/env python3
"""
FX バックテスト自動化パイプライン
===================================
yfinanceでFXデータを取得し、戦略を実行して
HTMLレポートを自動生成します。

依存ライブラリ:
    pip install yfinance pandas numpy

使い方:
    python fx_backtest_pipeline.py

カスタム戦略:
    Strategy クラスを継承して generate_signals() を実装してください。
"""

import json
import math
import datetime
import statistics
from pathlib import Path
from dataclasses import dataclass, field

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[警告] yfinance/pandas がインストールされていません")
    print("  pip install yfinance pandas numpy\n")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

CONFIG = {
    "symbol":        "USDJPY=X",   # yfinanceのFXティッカー (例: EURUSD=X)
    "start_date":    "2022-01-01",
    "end_date":      "2024-12-31",
    "interval":      "1d",          # 1d / 1h / 1wk
    "initial_capital": 1_000_000,  # 初期資金（円）
    "lot_size":      100_000,       # 1ロット
    "spread_pips":   0.3,           # スプレッド（pips）
    "commission":    0,             # 手数料（円/ロット）
    "output_file":   str(Path(__file__).parent / "fx_backtest_report.html"),
}

# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────

@dataclass
class Trade:
    entry_date:  str
    exit_date:   str
    direction:   str   # "BUY" or "SELL"
    entry_price: float
    exit_price:  float
    pnl_pips:    float
    pnl_amount:  float
    exit_reason: str   # "SL" or "TP" or "SIGNAL" or "END"


@dataclass
class BacktestResult:
    trades:          list[Trade] = field(default_factory=list)
    equity_curve:    list[float] = field(default_factory=list)
    dates:           list[str]   = field(default_factory=list)
    initial_capital: float = 1_000_000
    symbol:          str = ""
    strategy_name:   str = ""
    params:          dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# データ取得
# ─────────────────────────────────────────────

def fetch_data() -> list[dict]:
    """yfinanceからFXデータを取得する。"""
    if not YFINANCE_AVAILABLE:
        return generate_demo_prices()

    ticker = yf.Ticker(CONFIG["symbol"])
    df = ticker.history(
        start=CONFIG["start_date"],
        end=CONFIG["end_date"],
        interval=CONFIG["interval"],
    )
    if df.empty:
        print("[警告] データが取得できません。デモデータを使用します。")
        return generate_demo_prices()

    rows = []
    for idx, row in df.iterrows():
        rows.append({
            "date":  str(idx.date()),
            "open":  float(row["Open"]),
            "high":  float(row["High"]),
            "low":   float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row.get("Volume", 0)),
        })

    print(f"[データ取得] {len(rows)} バー取得完了 ({CONFIG['symbol']})")
    return rows


def generate_demo_prices() -> list[dict]:
    """デモ用の価格データを生成する。"""
    import random
    random.seed(777)
    rows = []
    price = 140.0
    start = datetime.date(2022, 1, 3)
    for i in range(750):
        date = start + datetime.timedelta(days=i)
        if date.weekday() >= 5:
            continue
        change = random.gauss(0, 0.5)
        price = max(100, price + change)
        spread = random.uniform(0.1, 0.5)
        rows.append({
            "date":  str(date),
            "open":  round(price - spread/2, 3),
            "high":  round(price + random.uniform(0.1, 0.8), 3),
            "low":   round(price - random.uniform(0.1, 0.8), 3),
            "close": round(price, 3),
            "volume": random.randint(50000, 200000),
        })
    return rows


# ─────────────────────────────────────────────
# 戦略クラス
# ─────────────────────────────────────────────

class Strategy:
    """基底戦略クラス。継承して使ってください。"""
    name = "Base"

    def generate_signals(self, data: list[dict]) -> list[str]:
        """
        シグナルを生成する。
        返り値: 各バーに対応する文字列リスト ["BUY", "SELL", "HOLD", "CLOSE"]
        """
        raise NotImplementedError


class MACrossStrategy(Strategy):
    """移動平均クロス戦略（ゴールデン/デッドクロス）。"""
    name = "MAクロス戦略"

    def __init__(self, fast_period=20, slow_period=50):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.params = {"fast_ma": fast_period, "slow_ma": slow_period}

    def _ema(self, closes: list[float], period: int) -> list[float]:
        emas = []
        k = 2 / (period + 1)
        ema = closes[0]
        for c in closes:
            ema = c * k + ema * (1 - k)
            emas.append(ema)
        return emas

    def generate_signals(self, data: list[dict]) -> list[str]:
        closes = [d["close"] for d in data]
        fast_emas = self._ema(closes, self.fast_period)
        slow_emas = self._ema(closes, self.slow_period)

        signals = ["HOLD"] * len(data)
        for i in range(1, len(data)):
            prev_diff = fast_emas[i-1] - slow_emas[i-1]
            curr_diff = fast_emas[i]   - slow_emas[i]
            if prev_diff <= 0 and curr_diff > 0:
                signals[i] = "BUY"
            elif prev_diff >= 0 and curr_diff < 0:
                signals[i] = "SELL"

        return signals


class RSIStrategy(Strategy):
    """RSI逆張り戦略。"""
    name = "RSI逆張り戦略"

    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        self.period    = rsi_period
        self.oversold  = oversold
        self.overbought = overbought
        self.params = {"rsi_period": rsi_period, "oversold": oversold, "overbought": overbought}

    def _rsi(self, closes: list[float]) -> list[float]:
        period = self.period
        rsis = [50.0] * period
        gains = [max(closes[i] - closes[i-1], 0) for i in range(1, len(closes))]
        losses = [max(closes[i-1] - closes[i], 0) for i in range(1, len(closes))]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for g, l in zip(gains[period:], losses[period:]):
            avg_gain = (avg_gain * (period-1) + g) / period
            avg_loss = (avg_loss * (period-1) + l) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsis.append(100 - 100/(1+rs))
        return rsis

    def generate_signals(self, data: list[dict]) -> list[str]:
        closes  = [d["close"] for d in data]
        rsis    = self._rsi(closes)
        signals = ["HOLD"] * len(data)
        for i in range(1, len(data)):
            if rsis[i-1] < self.oversold and rsis[i] >= self.oversold:
                signals[i] = "BUY"
            elif rsis[i-1] > self.overbought and rsis[i] <= self.overbought:
                signals[i] = "SELL"
        return signals


class BollingerBandStrategy(Strategy):
    """ボリンジャーバンド逆張り戦略。"""
    name = "ボリンジャーバンド戦略"

    def __init__(self, period=20, sigma=2.0):
        self.period = period
        self.sigma  = sigma
        self.params = {"period": period, "sigma": sigma}

    def generate_signals(self, data: list[dict]) -> list[str]:
        closes  = [d["close"] for d in data]
        signals = ["HOLD"] * len(data)

        for i in range(self.period, len(closes)):
            window = closes[i-self.period:i]
            mean   = sum(window) / len(window)
            std    = statistics.stdev(window)
            upper  = mean + self.sigma * std
            lower  = mean - self.sigma * std

            prev = closes[i-1]
            curr = closes[i]

            if prev <= lower and curr > lower:
                signals[i] = "BUY"
            elif prev >= upper and curr < upper:
                signals[i] = "SELL"

        return signals


# ─────────────────────────────────────────────
# バックテストエンジン
# ─────────────────────────────────────────────

class BacktestEngine:
    def __init__(self, strategy: Strategy, sl_pips=50, tp_pips=100):
        self.strategy  = strategy
        self.sl_pips   = sl_pips
        self.tp_pips   = tp_pips
        self.pip_value = 0.01  # JPYペアの場合

    def run(self, data: list[dict]) -> BacktestResult:
        """バックテストを実行する。"""
        result = BacktestResult(
            initial_capital = CONFIG["initial_capital"],
            symbol          = CONFIG["symbol"].replace("=X", ""),
            strategy_name   = self.strategy.name,
            params          = {
                **self.strategy.params,
                "sl_pips": self.sl_pips,
                "tp_pips": self.tp_pips,
            },
        )

        signals   = self.strategy.generate_signals(data)
        capital   = CONFIG["initial_capital"]
        position  = None  # {"direction": "BUY"/"SELL", "entry_price": float, "entry_date": str}
        spread    = CONFIG["spread_pips"] * self.pip_value

        for i, bar in enumerate(data):
            date  = bar["date"]
            close = bar["close"]
            high  = bar["high"]
            low   = bar["low"]

            # 既存ポジションのSL/TP確認
            if position is not None:
                ep = position["entry_price"]
                dir_ = position["direction"]

                sl_price = ep - self.sl_pips * self.pip_value if dir_ == "BUY" else ep + self.sl_pips * self.pip_value
                tp_price = ep + self.tp_pips * self.pip_value if dir_ == "BUY" else ep - self.tp_pips * self.pip_value

                exited = None
                exit_reason = None
                exit_price = close

                if dir_ == "BUY":
                    if low <= sl_price:
                        exited = True; exit_price = sl_price; exit_reason = "SL"
                    elif high >= tp_price:
                        exited = True; exit_price = tp_price; exit_reason = "TP"
                else:
                    if high >= sl_price:
                        exited = True; exit_price = sl_price; exit_reason = "SL"
                    elif low <= tp_price:
                        exited = True; exit_price = tp_price; exit_reason = "TP"

                # シグナルでクローズ
                sig = signals[i]
                if not exited and ((dir_ == "BUY" and sig == "SELL") or (dir_ == "SELL" and sig == "BUY")):
                    exited = True; exit_price = close; exit_reason = "SIGNAL"

                # 最終バー
                if not exited and i == len(data) - 1:
                    exited = True; exit_reason = "END"

                if exited:
                    pnl_pips = (exit_price - ep) / self.pip_value if dir_ == "BUY" else (ep - exit_price) / self.pip_value
                    pnl_pips -= CONFIG["spread_pips"]
                    pnl_amount = pnl_pips * self.pip_value * CONFIG["lot_size"]
                    capital += pnl_amount

                    result.trades.append(Trade(
                        entry_date  = position["entry_date"],
                        exit_date   = date,
                        direction   = dir_,
                        entry_price = ep,
                        exit_price  = exit_price,
                        pnl_pips    = round(pnl_pips, 1),
                        pnl_amount  = round(pnl_amount, 0),
                        exit_reason = exit_reason,
                    ))
                    position = None

            # 新規エントリー
            if position is None and signals[i] in ("BUY", "SELL"):
                ep = close + spread if signals[i] == "BUY" else close - spread
                position = {"direction": signals[i], "entry_price": ep, "entry_date": date}

            result.equity_curve.append(round(capital, 0))
            result.dates.append(date)

        return result


# ─────────────────────────────────────────────
# 統計計算
# ─────────────────────────────────────────────

def calc_stats(result: BacktestResult) -> dict:
    """バックテスト結果の統計を計算する。"""
    trades = result.trades
    if not trades:
        return {}

    pnls       = [t.pnl_amount for t in trades]
    wins       = [p for p in pnls if p > 0]
    losses     = [p for p in pnls if p <= 0]
    win_count  = len(wins)
    loss_count = len(losses)
    total      = len(trades)

    win_rate   = win_count / total * 100 if total > 0 else 0
    avg_win    = sum(wins) / win_count if wins else 0
    avg_loss   = abs(sum(losses) / loss_count) if losses else 0
    profit_factor = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else float("inf")

    # 最大ドローダウン
    equity = result.equity_curve
    peak = equity[0]
    max_dd = 0
    for e in equity:
        if e > peak:
            peak = e
        dd = (peak - e) / peak * 100
        if dd > max_dd:
            max_dd = dd

    # シャープレシオ（簡易）
    daily_rets = []
    for i in range(1, len(equity)):
        ret = (equity[i] - equity[i-1]) / equity[i-1]
        daily_rets.append(ret)
    if len(daily_rets) > 1 and statistics.stdev(daily_rets) > 0:
        sharpe = (statistics.mean(daily_rets) / statistics.stdev(daily_rets)) * math.sqrt(252)
    else:
        sharpe = 0

    final_capital = equity[-1] if equity else result.initial_capital
    total_return  = (final_capital - result.initial_capital) / result.initial_capital * 100

    return {
        "total_trades":   total,
        "win_count":      win_count,
        "loss_count":     loss_count,
        "win_rate":       round(win_rate, 1),
        "avg_win":        round(avg_win, 0),
        "avg_loss":       round(avg_loss, 0),
        "profit_factor":  round(profit_factor, 2),
        "max_drawdown":   round(max_dd, 1),
        "sharpe_ratio":   round(sharpe, 2),
        "total_return":   round(total_return, 1),
        "initial_capital": result.initial_capital,
        "final_capital":  round(final_capital, 0),
        "net_pnl":        round(final_capital - result.initial_capital, 0),
        "sl_exits":       sum(1 for t in trades if t.exit_reason == "SL"),
        "tp_exits":       sum(1 for t in trades if t.exit_reason == "TP"),
        "signal_exits":   sum(1 for t in trades if t.exit_reason == "SIGNAL"),
    }


# ─────────────────────────────────────────────
# HTMLレポート生成
# ─────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>バックテストレポート</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  :root{{--bg:#0d1117;--bg2:#161b22;--bg3:#21262d;--border:#30363d;
    --text:#e6edf3;--text2:#8b949e;--up:#3fb950;--down:#f85149;--accent:#58a6ff;--warn:#d29922;}}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;padding:0 0 40px;}}
  h1{{padding:20px 32px;font-size:20px;color:var(--accent);border-bottom:1px solid var(--border);background:var(--bg2);}}
  h2{{font-size:15px;color:var(--text2);margin-bottom:16px;}}
  .meta{{padding:8px 32px 16px;background:var(--bg2);border-bottom:1px solid var(--border);
    font-size:13px;color:var(--text2);}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;
    padding:20px 32px;}}
  .kpi{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px;}}
  .kpi-val{{font-size:26px;font-weight:700;margin-bottom:4px;}}
  .kpi-label{{font-size:11px;color:var(--text2);}}
  .pos{{color:var(--up);}} .neg{{color:var(--down);}} .neu{{color:var(--accent);}}
  .charts{{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:0 32px 24px;}}
  .chart-box{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:16px;}}
  canvas{{max-height:260px;}}
  .trade-table{{margin:0 32px;background:var(--bg2);border:1px solid var(--border);
    border-radius:8px;overflow:hidden;}}
  table{{width:100%;border-collapse:collapse;font-size:13px;}}
  th{{background:var(--bg3);color:var(--text2);padding:10px 14px;text-align:left;font-weight:500;}}
  td{{padding:8px 14px;border-top:1px solid var(--border);}}
  tr:hover td{{background:var(--bg3);}}
  .buy{{color:var(--up);font-weight:600;}}
  .sell{{color:var(--down);font-weight:600;}}
  @media(max-width:700px){{.charts{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<h1>📈 バックテストレポート — {strategy_name}</h1>
<div class="meta">
  シンボル: <b>{symbol}</b> &nbsp;|&nbsp;
  期間: {start} ～ {end} &nbsp;|&nbsp;
  パラメータ: {params} &nbsp;|&nbsp;
  生成日時: {generated}
</div>

<div class="kpi-grid">
  <div class="kpi"><div class="kpi-val {ret_cls}">{total_return}%</div><div class="kpi-label">総リターン</div></div>
  <div class="kpi"><div class="kpi-val {pnl_cls}">¥{net_pnl:,}</div><div class="kpi-label">純損益</div></div>
  <div class="kpi"><div class="kpi-val neu">{win_rate}%</div><div class="kpi-label">勝率</div></div>
  <div class="kpi"><div class="kpi-val neu">{profit_factor}</div><div class="kpi-label">プロフィットファクター</div></div>
  <div class="kpi"><div class="kpi-val neg">{max_drawdown}%</div><div class="kpi-label">最大ドローダウン</div></div>
  <div class="kpi"><div class="kpi-val neu">{sharpe_ratio}</div><div class="kpi-label">シャープレシオ</div></div>
  <div class="kpi"><div class="kpi-val">{total_trades}</div><div class="kpi-label">総トレード数</div></div>
  <div class="kpi"><div class="kpi-val">{win_count}勝 {loss_count}敗</div><div class="kpi-label">勝敗数</div></div>
</div>

<div class="charts">
  <div class="chart-box"><h2>📉 エクイティカーブ</h2><canvas id="equityChart"></canvas></div>
  <div class="chart-box"><h2>📊 月別損益</h2><canvas id="monthlyChart"></canvas></div>
  <div class="chart-box"><h2>🎯 損益分布</h2><canvas id="distChart"></canvas></div>
  <div class="chart-box"><h2>📋 出口理由</h2><canvas id="exitChart"></canvas></div>
</div>

<div class="trade-table">
  <table>
    <thead><tr>
      <th>#</th><th>方向</th><th>エントリー日</th><th>決済日</th>
      <th>エントリー価格</th><th>決済価格</th><th>損益(pips)</th><th>損益(¥)</th><th>出口理由</th>
    </tr></thead>
    <tbody>{trade_rows}</tbody>
  </table>
</div>

<script>
const eq = {equity_json};
const dates = {dates_json};
const monthly = {monthly_json};
const pnl_dist = {pnl_dist_json};
const exits = {exits_json};

// エクイティカーブ
new Chart(document.getElementById('equityChart'), {{
  type:'line',
  data:{{labels:dates,datasets:[{{label:'資産残高',data:eq,
    borderColor:'#58a6ff',backgroundColor:'rgba(88,166,255,.1)',
    borderWidth:1.5,pointRadius:0,fill:true,tension:.3}}]}},
  options:{{plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{color:'#8b949e',maxTicksLimit:8}},grid:{{color:'#21262d'}}}},
             y:{{ticks:{{color:'#8b949e',callback:v=>'¥'+v.toLocaleString()}},grid:{{color:'#21262d'}}}}}}}}
}});

// 月別損益
const mLabels = Object.keys(monthly);
const mVals   = Object.values(monthly);
new Chart(document.getElementById('monthlyChart'), {{
  type:'bar',
  data:{{labels:mLabels,datasets:[{{label:'月別損益',
    data:mVals,
    backgroundColor:mVals.map(v=>v>=0?'rgba(63,185,80,.7)':'rgba(248,81,73,.7)'),
    borderColor:mVals.map(v=>v>=0?'#3fb950':'#f85149'),
    borderWidth:1}}]}},
  options:{{plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{color:'#8b949e'}},grid:{{color:'#21262d'}}}},
             y:{{ticks:{{color:'#8b949e',callback:v=>'¥'+v.toLocaleString()}},grid:{{color:'#21262d'}}}}}}}}
}});

// 損益分布
new Chart(document.getElementById('distChart'), {{
  type:'bar',
  data:{{labels:pnl_dist.labels,datasets:[{{label:'トレード数',
    data:pnl_dist.counts,
    backgroundColor:pnl_dist.labels.map(l=>parseFloat(l)>=0?'rgba(63,185,80,.7)':'rgba(248,81,73,.7)'),
    borderWidth:0}}]}},
  options:{{plugins:{{legend:{{display:false}}}},
    scales:{{x:{{ticks:{{color:'#8b949e'}},grid:{{color:'#21262d'}}}},
             y:{{ticks:{{color:'#8b949e'}},grid:{{color:'#21262d'}}}}}}}}
}});

// 出口理由
new Chart(document.getElementById('exitChart'), {{
  type:'doughnut',
  data:{{labels:Object.keys(exits),datasets:[{{data:Object.values(exits),
    backgroundColor:['#f85149','#3fb950','#58a6ff','#d29922'],
    borderColor:'#21262d',borderWidth:2}}]}},
  options:{{plugins:{{legend:{{labels:{{color:'#e6edf3'}}}}}}}}
}});
</script>
</body>
</html>"""


def generate_html_report(result: BacktestResult, stats: dict, data: list[dict]) -> str:
    """HTMLレポートを生成する。"""
    # 月別損益
    monthly = {}
    for trade in result.trades:
        ym = trade.exit_date[:7]
        monthly[ym] = monthly.get(ym, 0) + trade.pnl_amount
    monthly = {k: round(v, 0) for k, v in sorted(monthly.items())}

    # 損益分布（ヒストグラム）
    pnls = [t.pnl_amount for t in result.trades]
    if pnls:
        min_p, max_p = min(pnls), max(pnls)
        bins = 10
        bin_size = (max_p - min_p) / bins if max_p != min_p else 1
        counts = [0] * bins
        labels = []
        for i in range(bins):
            low = min_p + i * bin_size
            labels.append(f"{low:.0f}")
            for p in pnls:
                if low <= p < low + bin_size or (i == bins-1 and p == max_p):
                    counts[i] += 1
        pnl_dist = {"labels": labels, "counts": counts}
    else:
        pnl_dist = {"labels": [], "counts": []}

    # 出口理由
    exits = {
        "SL": stats.get("sl_exits", 0),
        "TP": stats.get("tp_exits", 0),
        "シグナル": stats.get("signal_exits", 0),
    }

    # トレード行
    trade_rows = ""
    for i, t in enumerate(result.trades[-100:], 1):
        sign = "pos" if t.pnl_amount >= 0 else "neg"
        dir_cls = "buy" if t.direction == "BUY" else "sell"
        trade_rows += (
            f"<tr><td>{i}</td>"
            f"<td class='{dir_cls}'>{t.direction}</td>"
            f"<td>{t.entry_date}</td><td>{t.exit_date}</td>"
            f"<td>{t.entry_price:.4f}</td><td>{t.exit_price:.4f}</td>"
            f"<td class='{sign}'>{t.pnl_pips:+.1f}</td>"
            f"<td class='{sign}'>¥{t.pnl_amount:+,.0f}</td>"
            f"<td>{t.exit_reason}</td></tr>"
        )

    ret_cls = "pos" if stats.get("total_return", 0) >= 0 else "neg"
    pnl_cls = "pos" if stats.get("net_pnl", 0) >= 0 else "neg"

    return HTML_TEMPLATE.format(
        strategy_name = result.strategy_name,
        symbol        = result.symbol,
        start         = CONFIG["start_date"],
        end           = CONFIG["end_date"],
        params        = json.dumps(result.params, ensure_ascii=False),
        generated     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_return  = stats.get("total_return", 0),
        net_pnl       = int(stats.get("net_pnl", 0)),
        win_rate      = stats.get("win_rate", 0),
        profit_factor = stats.get("profit_factor", 0),
        max_drawdown  = stats.get("max_drawdown", 0),
        sharpe_ratio  = stats.get("sharpe_ratio", 0),
        total_trades  = stats.get("total_trades", 0),
        win_count     = stats.get("win_count", 0),
        loss_count    = stats.get("loss_count", 0),
        ret_cls       = ret_cls,
        pnl_cls       = pnl_cls,
        equity_json   = json.dumps(result.equity_curve),
        dates_json    = json.dumps(result.dates),
        monthly_json  = json.dumps(monthly),
        pnl_dist_json = json.dumps(pnl_dist),
        exits_json    = json.dumps(exits),
        trade_rows    = trade_rows,
    )


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────

def run_backtest(strategy: Strategy, sl_pips=50, tp_pips=100) -> tuple[BacktestResult, dict]:
    """戦略を実行してレポートを生成する。"""
    print(f"\n🚀 バックテスト開始: {strategy.name}")
    data = fetch_data()

    engine = BacktestEngine(strategy, sl_pips=sl_pips, tp_pips=tp_pips)
    result = engine.run(data)
    stats  = calc_stats(result)

    print(f"   総トレード数:      {stats.get('total_trades', 0)}")
    print(f"   勝率:              {stats.get('win_rate', 0)}%")
    print(f"   プロフィットファクター: {stats.get('profit_factor', 0)}")
    print(f"   最大ドローダウン:  {stats.get('max_drawdown', 0)}%")
    print(f"   総リターン:        {stats.get('total_return', 0)}%")
    print(f"   純損益:            ¥{stats.get('net_pnl', 0):,.0f}")

    html = generate_html_report(result, stats, data)
    output_path = CONFIG["output_file"]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ レポートを保存しました: {output_path}")

    return result, stats


def main():
    print("=" * 60)
    print("📊 FX バックテスト自動化パイプライン")
    print(f"   シンボル: {CONFIG['symbol']}")
    print(f"   期間: {CONFIG['start_date']} ～ {CONFIG['end_date']}")
    print("=" * 60)

    # ─── ここで使う戦略を選択 ───
    strategies = [
        (MACrossStrategy(fast_period=20, slow_period=50), 50, 100),
        # (RSIStrategy(rsi_period=14, oversold=30, overbought=70), 40, 80),
        # (BollingerBandStrategy(period=20, sigma=2.0), 45, 90),
    ]

    for strategy, sl, tp in strategies:
        run_backtest(strategy, sl_pips=sl, tp_pips=tp)


if __name__ == "__main__":
    main()
