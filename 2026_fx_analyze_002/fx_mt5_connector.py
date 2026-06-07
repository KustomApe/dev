#!/usr/bin/env python3
"""
MT5 マルチタイムフレームコネクター
====================================
MetaTrader5 Python ライブラリを使って複数タイムフレームの
テクニカル分析データを取得し、ダッシュボード用JSONを出力します。

依存ライブラリ:
    pip install MetaTrader5 pandas numpy

使い方:
    python fx_mt5_connector.py
    → fx_mtf_data.json を生成 → ダッシュボードが読み込む

MT5が起動している必要があります。
"""

import json
import time
import math
import datetime
from pathlib import Path

# MT5ライブラリ (インストール済みの場合はTrue)
try:
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("[警告] MetaTrader5 / pandas がインストールされていません")
    print("  pip install MetaTrader5 pandas numpy")
    print("  デモモードで起動します\n")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

CONFIG = {
    "symbols": [
        "USDJPY", "EURUSD", "GBPUSD", "AUDUSD",
        "USDCAD", "NZDUSD", "USDCHF", "EURJPY",
    ],
    "timeframes": {
        "M15": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 1,
        "H1":  mt5.TIMEFRAME_H1  if MT5_AVAILABLE else 2,
        "H4":  mt5.TIMEFRAME_H4  if MT5_AVAILABLE else 3,
        "D1":  mt5.TIMEFRAME_D1  if MT5_AVAILABLE else 4,
    },
    "bars": 200,            # 取得するバー数
    "fast_ma": 21,          # 短期EMA
    "slow_ma": 50,          # 長期EMA
    "atr_period": 14,       # ATR期間
    "rsi_period": 14,       # RSI期間
    "output_file": str(Path(__file__).parent / "fx_mtf_data.json"),
    "refresh_seconds": 60,  # 更新間隔
}

# ─────────────────────────────────────────────
# テクニカル指標計算
# ─────────────────────────────────────────────

def calc_ema(closes: list[float], period: int) -> float:
    """EMAを計算して最新値を返す。"""
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = closes[0]
    for c in closes[1:]:
        ema = c * k + ema * (1 - k)
    return ema


def calc_atr(highs, lows, closes, period: int) -> float:
    """ATR（Average True Range）を計算する。"""
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    if not trs:
        return 0.0
    # Wilder's smoothing
    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def calc_rsi(closes: list[float], period: int) -> float:
    """RSIを計算する。"""
    if len(closes) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i-1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def determine_trend(fast_ema: float, slow_ema: float, rsi: float) -> dict:
    """トレンド方向と強さを判定する。"""
    if fast_ema > slow_ema:
        direction = "UP"
        strength = min(100, int((fast_ema - slow_ema) / slow_ema * 10000))
    elif fast_ema < slow_ema:
        direction = "DOWN"
        strength = min(100, int((slow_ema - fast_ema) / slow_ema * 10000))
    else:
        direction = "NEUTRAL"
        strength = 0

    # RSIによる過熱感
    if rsi > 70:
        overheat = "過買い"
    elif rsi < 30:
        overheat = "過売り"
    else:
        overheat = "中立"

    return {
        "direction": direction,
        "strength": strength,
        "rsi": round(rsi, 1),
        "overheat": overheat,
    }


# ─────────────────────────────────────────────
# MT5データ取得
# ─────────────────────────────────────────────

def get_rates_mt5(symbol: str, tf_value: int, count: int) -> list[dict] | None:
    """MT5からレートデータを取得する。"""
    rates = mt5.copy_rates_from_pos(symbol, tf_value, 0, count)
    if rates is None or len(rates) == 0:
        return None
    return [
        {
            "time":  r[0],
            "open":  r[1],
            "high":  r[2],
            "low":   r[3],
            "close": r[4],
        }
        for r in rates
    ]


def analyze_symbol_mt5(symbol: str) -> dict:
    """1シンボルの全タイムフレームを分析する。"""
    timeframes = {}
    for tf_name, tf_value in CONFIG["timeframes"].items():
        rates = get_rates_mt5(symbol, tf_value, CONFIG["bars"])
        if rates is None:
            timeframes[tf_name] = {"error": "データ取得失敗"}
            continue

        closes = [r["close"] for r in rates]
        highs  = [r["high"]  for r in rates]
        lows   = [r["low"]   for r in rates]

        fast_ema = calc_ema(closes, CONFIG["fast_ma"])
        slow_ema = calc_ema(closes, CONFIG["slow_ma"])
        rsi      = calc_rsi(closes, CONFIG["rsi_period"])
        atr      = calc_atr(highs, lows, closes, CONFIG["atr_period"])
        trend    = determine_trend(fast_ema, slow_ema, rsi)

        timeframes[tf_name] = {
            **trend,
            "close":    round(closes[-1], 5),
            "fast_ema": round(fast_ema, 5),
            "slow_ema": round(slow_ema, 5),
            "atr":      round(atr, 5),
        }

    # タイムフレーム一致スコア（全TFが同じ方向なら高スコア）
    directions = [v.get("direction") for v in timeframes.values() if "direction" in v]
    up_count   = directions.count("UP")
    down_count = directions.count("DOWN")
    total      = len(directions)
    if total == 0:
        alignment = 0
        primary_direction = "NEUTRAL"
    elif up_count >= down_count:
        alignment = int(up_count / total * 100)
        primary_direction = "UP" if up_count > down_count else "NEUTRAL"
    else:
        alignment = int(down_count / total * 100)
        primary_direction = "DOWN"

    # 現在価格の取得
    tick = mt5.symbol_info_tick(symbol)
    current_price = tick.ask if tick else 0

    return {
        "symbol":            symbol,
        "current_price":     round(current_price, 5),
        "primary_direction": primary_direction,
        "alignment":         alignment,
        "timeframes":        timeframes,
    }


# ─────────────────────────────────────────────
# デモデータ生成
# ─────────────────────────────────────────────

def generate_demo_data() -> list[dict]:
    """MT5未接続時のデモデータを生成する。"""
    import random
    random.seed(42)

    demo_prices = {
        "USDJPY": 149.85, "EURUSD": 1.0872, "GBPUSD": 1.2654,
        "AUDUSD": 0.6521, "USDCAD": 1.3612, "NZDUSD": 0.5987,
        "USDCHF": 0.8934, "EURJPY": 162.73,
    }
    scenarios = [
        {"direction": "UP",   "strength": random.randint(40, 90)},
        {"direction": "DOWN", "strength": random.randint(40, 90)},
        {"direction": "UP",   "strength": random.randint(20, 60)},
        {"direction": "NEUTRAL", "strength": 0},
    ]

    result = []
    for sym in CONFIG["symbols"]:
        base = demo_prices.get(sym, 1.0000)
        tfs = {}
        directions_used = []
        for tf in CONFIG["timeframes"]:
            sc = random.choice(scenarios)
            rsi_val = random.uniform(30, 70)
            if sc["direction"] == "UP":
                rsi_val = random.uniform(50, 80)
            elif sc["direction"] == "DOWN":
                rsi_val = random.uniform(20, 50)
            tfs[tf] = {
                "direction": sc["direction"],
                "strength":  sc["strength"],
                "rsi":       round(rsi_val, 1),
                "overheat":  "過買い" if rsi_val > 70 else "過売り" if rsi_val < 30 else "中立",
                "close":     round(base + random.uniform(-0.001, 0.001), 5),
                "fast_ema":  round(base + random.uniform(-0.002, 0.002), 5),
                "slow_ema":  round(base + random.uniform(-0.004, 0.004), 5),
                "atr":       round(random.uniform(0.0005, 0.002), 5),
            }
            directions_used.append(sc["direction"])

        up_c   = directions_used.count("UP")
        dn_c   = directions_used.count("DOWN")
        total  = len(directions_used)
        if up_c > dn_c:
            pdir = "UP"; aln = int(up_c / total * 100)
        elif dn_c > up_c:
            pdir = "DOWN"; aln = int(dn_c / total * 100)
        else:
            pdir = "NEUTRAL"; aln = 0

        result.append({
            "symbol":            sym,
            "current_price":     round(base + random.uniform(-0.001, 0.001), 5),
            "primary_direction": pdir,
            "alignment":         aln,
            "timeframes":        tfs,
        })
    return result


# ─────────────────────────────────────────────
# JSON出力
# ─────────────────────────────────────────────

def save_data(data: list[dict]):
    """データをJSONファイルに保存する。"""
    output = {
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_demo":    not MT5_AVAILABLE,
        "symbols":    data,
    }
    with open(CONFIG["output_file"], "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[保存] {CONFIG['output_file']}")


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────

def run_once():
    """1回分析を実行してJSONを保存する。"""
    if MT5_AVAILABLE:
        if not mt5.initialize():
            print("[エラー] MT5初期化失敗。MT5を起動してください。")
            return
        data = [analyze_symbol_mt5(sym) for sym in CONFIG["symbols"]]
        mt5.shutdown()
    else:
        data = generate_demo_data()

    save_data(data)

    # 整合スコア順に表示
    print("\n📊 マルチタイムフレーム分析結果")
    print(f"{'シンボル':<10} {'方向':<8} {'一致度':>5} {'M15':^7} {'H1':^7} {'H4':^7} {'D1':^7}")
    print("-" * 60)
    for sym_data in sorted(data, key=lambda x: x["alignment"], reverse=True):
        dir_icon = {"UP": "▲", "DOWN": "▼", "NEUTRAL": "─"}.get(
            sym_data["primary_direction"], "─"
        )
        tf_icons = " ".join(
            {"UP": "▲", "DOWN": "▼", "NEUTRAL": "─"}.get(
                sym_data["timeframes"].get(tf, {}).get("direction", "─"), "─"
            )
            for tf in CONFIG["timeframes"]
        )
        print(
            f"{sym_data['symbol']:<10} "
            f"{dir_icon} {sym_data['primary_direction']:<6} "
            f"{sym_data['alignment']:>4}%  "
            f"{tf_icons}"
        )


def main():
    print("=" * 60)
    print("📡 MT5 マルチタイムフレームコネクター")
    print(f"   更新間隔: {CONFIG['refresh_seconds']}秒")
    print(f"   出力先: {CONFIG['output_file']}")
    print("=" * 60)

    while True:
        try:
            run_once()
            print(f"⏳ {CONFIG['refresh_seconds']}秒後に更新... (Ctrl+C で終了)")
            time.sleep(CONFIG["refresh_seconds"])
        except KeyboardInterrupt:
            print("\n\n👋 コネクターを終了しました")
            break
        except Exception as e:
            print(f"[エラー] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
