"""
USDJPY FX トレード分析ツール
================================
使用インジケーター: MA/EMA, RSI, MACD, ボリンジャーバンド
データソース: Yahoo Finance (yfinance)
出力: インタラクティブHTMLチャート

必要ライブラリのインストール:
    pip install yfinance pandas numpy plotly

実行方法:
    python usdjpy_analyzer.py
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
import sys
from datetime import datetime


# ============================================================
#  設定パラメーター
# ============================================================
CONFIG = {
    "ticker":        "USDJPY=X",       # 通貨ペア
    "period":        "6mo",            # データ期間: 1mo/3mo/6mo/1y/2y
    "interval":      "1d",             # 足種: 1m/5m/15m/1h/1d/1wk
    # 移動平均
    "ma_short":      20,               # 短期MA期間
    "ma_long":       50,               # 長期MA期間
    # EMA (MACD用)
    "ema_fast":      12,
    "ema_slow":      26,
    "ema_signal":    9,
    # RSI
    "rsi_period":    14,
    "rsi_overbuy":   70,               # 過買い閾値
    "rsi_oversell":  30,               # 過売り閾値
    # ボリンジャーバンド
    "bb_period":     20,
    "bb_std":        2,
    # シグナル判定
    "signal_buy_th":  2,               # 買いシグナルのスコア閾値
    "signal_sell_th": -2,              # 売りシグナルのスコア閾値
}


# ============================================================
#  データ取得
# ============================================================
def fetch_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    print(f"[データ取得] {ticker}  期間:{period}  足:{interval} ...")
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        print("エラー: データを取得できませんでした。インターネット接続を確認してください。")
        sys.exit(1)
    # カラム名をフラット化（MultiIndexの場合）
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    print(f"  → {len(df)} 本のローソク足を取得")
    return df


# ============================================================
#  テクニカルインジケーター計算
# ============================================================
def calculate_indicators(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    close = df["Close"]

    # ── 移動平均線 ──
    df["MA_S"]  = close.rolling(cfg["ma_short"]).mean()
    df["MA_L"]  = close.rolling(cfg["ma_long"]).mean()

    # ── EMA ──
    df["EMA_F"] = close.ewm(span=cfg["ema_fast"],   adjust=False).mean()
    df["EMA_S"] = close.ewm(span=cfg["ema_slow"],   adjust=False).mean()

    # ── MACD ──
    df["MACD"]       = df["EMA_F"] - df["EMA_S"]
    df["MACD_Sig"]   = df["MACD"].ewm(span=cfg["ema_signal"], adjust=False).mean()
    df["MACD_Hist"]  = df["MACD"] - df["MACD_Sig"]

    # ── RSI ──
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(cfg["rsi_period"]).mean()
    loss  = (-delta.clip(upper=0)).rolling(cfg["rsi_period"]).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ── ボリンジャーバンド ──
    bb_mid       = close.rolling(cfg["bb_period"]).mean()
    bb_std       = close.rolling(cfg["bb_period"]).std()
    df["BB_Mid"] = bb_mid
    df["BB_Up"]  = bb_mid + cfg["bb_std"] * bb_std
    df["BB_Lo"]  = bb_mid - cfg["bb_std"] * bb_std
    df["BB_BW"]  = (df["BB_Up"] - df["BB_Lo"]) / bb_mid * 100  # バンド幅(%)

    df.dropna(inplace=True)
    return df


# ============================================================
#  売買シグナル生成
# ============================================================
def generate_signals(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    スコアリング方式でシグナルを生成。
    各インジケーターが買い/売りを示すと +1/-1 を加算 (重み付き)。
    スコア >= buy_th  → 総合買いシグナル
    スコア <= sell_th → 総合売りシグナル
    """
    score = pd.Series(0, index=df.index, dtype=float)
    details = {}

    # ① MAゴールデン/デッドクロス (重み: ±2)
    ma_cross_up   = (df["MA_S"] > df["MA_L"]) & (df["MA_S"].shift(1) <= df["MA_L"].shift(1))
    ma_cross_down = (df["MA_S"] < df["MA_L"]) & (df["MA_S"].shift(1) >= df["MA_L"].shift(1))
    score += ma_cross_up.astype(float)   * 2
    score -= ma_cross_down.astype(float) * 2
    # トレンド追従 (短期>長期なら+0.5)
    score += ((df["MA_S"] > df["MA_L"]).astype(float) * 0.5)
    score -= ((df["MA_S"] < df["MA_L"]).astype(float) * 0.5)
    details["MA_Cross_Buy"]  = ma_cross_up
    details["MA_Cross_Sell"] = ma_cross_down

    # ② MACDクロス (重み: ±2)
    macd_cross_up   = (df["MACD"] > df["MACD_Sig"]) & (df["MACD"].shift(1) <= df["MACD_Sig"].shift(1))
    macd_cross_down = (df["MACD"] < df["MACD_Sig"]) & (df["MACD"].shift(1) >= df["MACD_Sig"].shift(1))
    score += macd_cross_up.astype(float)   * 2
    score -= macd_cross_down.astype(float) * 2
    details["MACD_Cross_Buy"]  = macd_cross_up
    details["MACD_Cross_Sell"] = macd_cross_down

    # ③ RSI (重み: ±1.5)
    rsi_buy  = df["RSI"] < cfg["rsi_oversell"]
    rsi_sell = df["RSI"] > cfg["rsi_overbuy"]
    score += rsi_buy.astype(float)  * 1.5
    score -= rsi_sell.astype(float) * 1.5
    details["RSI_Buy"]  = rsi_buy
    details["RSI_Sell"] = rsi_sell

    # ④ ボリンジャーバンド タッチ (重み: ±1)
    bb_buy  = df["Close"] <= df["BB_Lo"]
    bb_sell = df["Close"] >= df["BB_Up"]
    score += bb_buy.astype(float)
    score -= bb_sell.astype(float)
    details["BB_Buy"]  = bb_buy
    details["BB_Sell"] = bb_sell

    df["Score"] = score
    df["Buy_Signal"]  = score >= cfg["signal_buy_th"]
    df["Sell_Signal"] = score <= cfg["signal_sell_th"]

    for k, v in details.items():
        df[k] = v

    buy_count  = df["Buy_Signal"].sum()
    sell_count = df["Sell_Signal"].sum()
    print(f"[シグナル] 買い:{buy_count}回  売り:{sell_count}回")
    return df


# ============================================================
#  チャート作成
# ============================================================
def build_chart(df: pd.DataFrame, cfg: dict) -> go.Figure:
    # ── レイアウト ──
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        subplot_titles=[
            f"USDJPY ローソク足 + MA({cfg['ma_short']}/{cfg['ma_long']}) + ボリンジャーバンド",
            f"MACD ({cfg['ema_fast']},{cfg['ema_slow']},{cfg['ema_signal']})",
            f"RSI ({cfg['rsi_period']})",
            "シグナルスコア",
        ],
        row_heights=[0.50, 0.18, 0.16, 0.16],
    )

    idx = df.index

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  ROW 1: ローソク足 + MA + BB
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fig.add_trace(go.Candlestick(
        x=idx,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name="USDJPY",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        increasing_fillcolor="#26a69a",
        decreasing_fillcolor="#ef5350",
    ), row=1, col=1)

    # MA
    fig.add_trace(go.Scatter(
        x=idx, y=df["MA_S"],
        name=f"MA{cfg['ma_short']}",
        line=dict(color="#42a5f5", width=1.8),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["MA_L"],
        name=f"MA{cfg['ma_long']}",
        line=dict(color="#ff9800", width=1.8),
    ), row=1, col=1)

    # ボリンジャーバンド
    fig.add_trace(go.Scatter(
        x=idx, y=df["BB_Up"],
        name="BB Upper",
        line=dict(color="rgba(180,180,180,0.7)", dash="dot", width=1.2),
        showlegend=True,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["BB_Lo"],
        name="BB Lower",
        line=dict(color="rgba(180,180,180,0.7)", dash="dot", width=1.2),
        fill="tonexty",
        fillcolor="rgba(180,180,180,0.06)",
        showlegend=True,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["BB_Mid"],
        name="BB Mid",
        line=dict(color="rgba(180,180,180,0.4)", dash="dash", width=1),
    ), row=1, col=1)

    # 買いシグナルマーカー
    buy_df  = df[df["Buy_Signal"]]
    sell_df = df[df["Sell_Signal"]]

    fig.add_trace(go.Scatter(
        x=buy_df.index,
        y=buy_df["Low"] * 0.9994,
        mode="markers+text",
        name="買いシグナル",
        marker=dict(symbol="triangle-up", size=14, color="#00e676",
                    line=dict(color="white", width=0.8)),
        text=["BUY"] * len(buy_df),
        textposition="bottom center",
        textfont=dict(size=9, color="#00e676"),
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=sell_df.index,
        y=sell_df["High"] * 1.0006,
        mode="markers+text",
        name="売りシグナル",
        marker=dict(symbol="triangle-down", size=14, color="#ff1744",
                    line=dict(color="white", width=0.8)),
        text=["SELL"] * len(sell_df),
        textposition="top center",
        textfont=dict(size=9, color="#ff1744"),
    ), row=1, col=1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  ROW 2: MACD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    hist_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(
        x=idx, y=df["MACD_Hist"],
        name="MACD Hist",
        marker_color=hist_colors,
        opacity=0.7,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["MACD"],
        name="MACD",
        line=dict(color="#42a5f5", width=1.6),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["MACD_Sig"],
        name="Signal",
        line=dict(color="#ff9800", width=1.6),
    ), row=2, col=1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  ROW 3: RSI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fig.add_trace(go.Scatter(
        x=idx, y=df["RSI"],
        name="RSI",
        line=dict(color="#ab47bc", width=1.8),
        fill="tozeroy",
        fillcolor="rgba(171,71,188,0.08)",
    ), row=3, col=1)
    # 閾値ライン
    for y_val, color, label in [
        (cfg["rsi_overbuy"],  "#ef5350", f"過買い({cfg['rsi_overbuy']})"),
        (cfg["rsi_oversell"], "#26a69a", f"過売り({cfg['rsi_oversell']})"),
        (50, "rgba(200,200,200,0.3)", "中立(50)"),
    ]:
        fig.add_hline(y=y_val, line_dash="dash", line_color=color,
                      line_width=1.2, row=3, col=1,
                      annotation_text=label, annotation_position="right",
                      annotation_font_size=10)
    # 過買い/過売りゾーン塗り
    fig.add_hrect(y0=cfg["rsi_overbuy"], y1=100,
                  fillcolor="rgba(239,83,80,0.08)", line_width=0, row=3, col=1)
    fig.add_hrect(y0=0, y1=cfg["rsi_oversell"],
                  fillcolor="rgba(38,166,154,0.08)", line_width=0, row=3, col=1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  ROW 4: スコア棒グラフ
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    score_colors = [
        "#00e676" if v >= cfg["signal_buy_th"] else
        "#ff1744" if v <= cfg["signal_sell_th"] else
        "rgba(150,150,150,0.6)"
        for v in df["Score"]
    ]
    fig.add_trace(go.Bar(
        x=idx, y=df["Score"],
        name="シグナルスコア",
        marker_color=score_colors,
        opacity=0.85,
    ), row=4, col=1)
    for th, color, label in [
        (cfg["signal_buy_th"],  "#00e676", f"買い閾値(+{cfg['signal_buy_th']})"),
        (cfg["signal_sell_th"], "#ff1744", f"売り閾値({cfg['signal_sell_th']})"),
    ]:
        fig.add_hline(y=th, line_dash="dash", line_color=color,
                      line_width=1.2, row=4, col=1,
                      annotation_text=label, annotation_position="right",
                      annotation_font_size=10)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  全体レイアウト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    latest        = df["Close"].iloc[-1]
    latest_rsi    = df["RSI"].iloc[-1]
    latest_macd   = df["MACD"].iloc[-1]
    latest_score  = df["Score"].iloc[-1]

    if latest_score >= cfg["signal_buy_th"]:
        current_signal = "🟢 買い"
    elif latest_score <= cfg["signal_sell_th"]:
        current_signal = "🔴 売り"
    else:
        current_signal = "⚪ 様子見"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    fig.update_layout(
        title=dict(
            text=(
                f"<b>USDJPY FX トレード分析ダッシュボード</b>"
                f"<br><sup>更新: {now_str} ／ "
                f"現在値: {latest:.3f}円 ／ "
                f"RSI: {latest_rsi:.1f} ／ "
                f"MACD: {latest_macd:.4f} ／ "
                f"シグナル: {current_signal} (スコア: {latest_score:+.1f})</sup>"
            ),
            font=dict(size=16),
        ),
        template="plotly_dark",
        height=960,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left",   x=0,
            font=dict(size=11),
        ),
        margin=dict(l=60, r=120, t=110, b=40),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )

    # Y軸ラベル
    fig.update_yaxes(title_text="円 (JPY)", row=1, col=1)
    fig.update_yaxes(title_text="MACD",     row=2, col=1)
    fig.update_yaxes(title_text="RSI",      row=3, col=1, range=[0, 100])
    fig.update_yaxes(title_text="スコア",    row=4, col=1)

    # 横軸の非表示設定（最下段のみ表示）
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=3, col=1)

    return fig


# ============================================================
#  シグナルサマリーをコンソール出力
# ============================================================
def print_summary(df: pd.DataFrame, cfg: dict):
    print("\n" + "=" * 55)
    print("  USDJPY トレード分析サマリー")
    print("=" * 55)
    latest = df.iloc[-1]
    score  = latest["Score"]

    print(f"  現在値   : {latest['Close']:.3f} 円")
    print(f"  MA{cfg['ma_short']}      : {latest['MA_S']:.3f}")
    print(f"  MA{cfg['ma_long']}      : {latest['MA_L']:.3f}")
    print(f"  RSI      : {latest['RSI']:.1f}")
    print(f"  MACD     : {latest['MACD']:.4f}  Signal: {latest['MACD_Sig']:.4f}")
    print(f"  BB上限   : {latest['BB_Up']:.3f}  BB下限: {latest['BB_Lo']:.3f}")
    print(f"  スコア   : {score:+.1f}")
    print("-" * 55)

    if score >= cfg["signal_buy_th"]:
        print(f"  ✅ 総合シグナル: 【買い】 (スコア {score:+.1f})")
    elif score <= cfg["signal_sell_th"]:
        print(f"  ❌ 総合シグナル: 【売り】 (スコア {score:+.1f})")
    else:
        print(f"  ⏸  総合シグナル: 【様子見】 (スコア {score:+.1f})")

    print("-" * 55)
    print("  インジケーター内訳:")
    checks = [
        ("MA クロス(買)",  latest.get("MA_Cross_Buy",   False)),
        ("MA クロス(売)",  latest.get("MA_Cross_Sell",  False)),
        ("MACD クロス(買)", latest.get("MACD_Cross_Buy",  False)),
        ("MACD クロス(売)", latest.get("MACD_Cross_Sell", False)),
        (f"RSI 過売り(<{cfg['rsi_oversell']})", latest.get("RSI_Buy",  False)),
        (f"RSI 過買い(>{cfg['rsi_overbuy']})",  latest.get("RSI_Sell", False)),
        ("BB 下限タッチ(買)", latest.get("BB_Buy",  False)),
        ("BB 上限タッチ(売)", latest.get("BB_Sell", False)),
    ]
    for name, val in checks:
        mark = "●" if val else "○"
        print(f"    {mark} {name}")

    # 直近シグナル履歴
    recent_buy  = df[df["Buy_Signal"]].tail(3)
    recent_sell = df[df["Sell_Signal"]].tail(3)
    print("-" * 55)
    print("  直近の買いシグナル:")
    if len(recent_buy) == 0:
        print("    (なし)")
    else:
        for dt, row in recent_buy.iterrows():
            print(f"    {str(dt)[:10]}  終値: {row['Close']:.3f}  スコア: {row['Score']:+.1f}")
    print("  直近の売りシグナル:")
    if len(recent_sell) == 0:
        print("    (なし)")
    else:
        for dt, row in recent_sell.iterrows():
            print(f"    {str(dt)[:10]}  終値: {row['Close']:.3f}  スコア: {row['Score']:+.1f}")
    print("=" * 55)
    print()


# ============================================================
#  メイン
# ============================================================
def main():
    print("=" * 55)
    print("  USDJPY FX トレード分析ツール")
    print("=" * 55)

    # ─ データ取得 ─
    df = fetch_data(CONFIG["ticker"], CONFIG["period"], CONFIG["interval"])

    # ─ インジケーター計算 ─
    print("[計算] テクニカルインジケーターを計算中 ...")
    df = calculate_indicators(df, CONFIG)

    # ─ シグナル生成 ─
    df = generate_signals(df, CONFIG)

    # ─ サマリー出力 ─
    print_summary(df, CONFIG)

    # ─ チャート作成 ─
    print("[チャート] インタラクティブチャートを生成中 ...")
    fig = build_chart(df, CONFIG)

    # ─ HTML出力 ─
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usdjpy_chart.html")
    fig.write_html(
        out_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        },
    )
    print(f"[完了] チャートを保存しました: {out_path}")

    # ─ ブラウザで開く ─
    webbrowser.open(f"file://{out_path}")
    print("ブラウザでチャートが開きました。")


if __name__ == "__main__":
    main()
