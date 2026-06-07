"""
FX / 先物 / コモディティ トレード分析 Webアプリ
================================================
マルチ銘柄対応・足種切り替え・1分自動更新・Discord Webhook通知

ライブラリのインストール:
    pip install dash dash-bootstrap-components yfinance pandas numpy plotly requests

起動:
    python fx_analyzer_webapp.py

アクセス:
    http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import requests
import threading
import json
import logging

logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


# ============================================================
#  ① 設定
# ============================================================
DISCORD_WEBHOOK_URL = ""   # ここに直接書くか、UI設定パネルで入力
PORT        = 8050
REFRESH_MS  = 60_000
DEFAULT_SYMBOL = "USDJPY=X"
DEFAULT_TF     = "1h"


# ============================================================
#  ② 銘柄マスター  ※ 同じtickerを複数カテゴリに入れないこと
# ============================================================
INSTRUMENTS = {
    "FX 主要": {
        "USDJPY=X": "USD/JPY",
        "EURUSD=X": "EUR/USD",
        "GBPUSD=X": "GBP/USD",
        "AUDUSD=X": "AUD/USD",
        "USDCHF=X": "USD/CHF",
        "USDCAD=X": "USD/CAD",
    },
    "FX クロス円": {
        "EURJPY=X": "EUR/JPY",
        "GBPJPY=X": "GBP/JPY",
        "AUDJPY=X": "AUD/JPY",
        "CADJPY=X": "CAD/JPY",
        "CHFJPY=X": "CHF/JPY",
    },
    "先物": {
        "ES=F":  "S&P500先物",
        "NQ=F":  "NASDAQ先物",
        "YM=F":  "NYダウ先物",
        "NKD=F": "日経225先物",
        "GC=F":  "金先物",
        "ZB=F":  "米国債30年先物",
    },
    "コモディティ": {
        "CL=F":     "WTI原油",
        "NG=F":     "天然ガス",
        "SI=F":     "銀",
        "XAUUSD=X": "ゴールド(現物)",   # ← GC=F重複を避けXAUUSD=Xに変更
        "HG=F":     "銅",
        "ZW=F":     "小麦",
    },
}

# フラット辞書（ticker → 表示名）
ALL_SYMBOLS: dict = {}
for _cat, _syms in INSTRUMENTS.items():
    ALL_SYMBOLS.update(_syms)

# サイドバー表示順（INSTRUMENTS定義順）
SIDEBAR_ORDER = [t for cat in INSTRUMENTS.values() for t in cat]


# ============================================================
#  ③ 足種プリセット
# ============================================================
TIMEFRAMES = {
    "15m": {"label": "15分", "interval": "15m", "period": "5d"},
    "1h":  {"label": "1時間", "interval": "1h",  "period": "60d"},
    "4h":  {"label": "4時間", "interval": "1h",  "period": "60d"},
    "1d":  {"label": "日足",  "interval": "1d",  "period": "6mo"},
    "1wk": {"label": "週足",  "interval": "1wk", "period": "2y"},
}


# ============================================================
#  ④ インジケーターパラメーター
# ============================================================
PARAMS = {
    "ma_short": 20, "ma_long": 50,
    "ema_fast": 12, "ema_slow": 26, "ema_signal": 9,
    "rsi_period": 14, "rsi_overbuy": 70, "rsi_oversell": 30,
    "bb_period": 20, "bb_std": 2.0,
    "buy_th": 2.0, "sell_th": -2.0,
}


# ============================================================
#  ⑤ カラー / スタイル定数
# ============================================================
C = {
    "bg_base":     "#0d1117",
    "bg_panel":    "#161b22",
    "border":      "#30363d",
    "text_main":   "#e6edf3",
    "text_muted":  "#8b949e",
    "green":       "#26a69a",
    "bright_green":"#00e676",
    "red":         "#ef5350",
    "bright_red":  "#ff1744",
    "blue":        "#42a5f5",
    "orange":      "#ffa726",
}

CSS = {
    "stat_card": {
        "background": C["bg_panel"], "border": f"1px solid {C['border']}",
        "borderRadius": "8px", "padding": "10px 13px",
        "display": "flex", "flexDirection": "column", "justifyContent": "center",
    },
    "stat_label": {"fontSize": "10px", "color": C["text_muted"], "marginBottom": "3px"},
    "stat_value": {"fontSize": "20px", "fontWeight": "700",
                   "color": C["text_main"], "lineHeight": "1"},
    "stat_sub":   {"fontSize": "10px", "color": C["text_muted"], "marginTop": "2px"},
    "hist_row": {
        "display": "flex", "alignItems": "center", "gap": "10px",
        "padding": "5px 10px", "background": C["bg_panel"],
        "border": f"1px solid {C['border']}", "borderRadius": "6px",
        "marginBottom": "4px", "fontSize": "11px", "color": C["text_main"],
    },
    "sym_btn": {
        "display": "block", "width": "100%", "textAlign": "left",
        "padding": "5px 10px", "marginBottom": "2px",
        "background": "transparent", "border": "none",
        "borderRadius": "5px", "cursor": "pointer",
        "fontSize": "12px", "color": C["text_muted"],
        "transition": "background 0.15s",
    },
    "sym_btn_active": {
        "display": "block", "width": "100%", "textAlign": "left",
        "padding": "5px 10px", "marginBottom": "2px",
        "background": "rgba(66,165,245,0.14)", "border": "none",
        "borderRadius": "5px", "cursor": "pointer",
        "fontSize": "12px", "color": C["text_main"],
        "fontWeight": "700", "transition": "background 0.15s",
    },
}


# ============================================================
#  ⑥ データ取得
# ============================================================
def fetch_ohlcv(ticker: str, tf_key: str) -> pd.DataFrame:
    cfg = TIMEFRAMES[tf_key]
    df = yf.download(ticker, period=cfg["period"], interval=cfg["interval"],
                     progress=False, auto_adjust=True)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)
    if tf_key == "4h":
        df = df.resample("4h").agg({
            "Open": "first", "High": "max",
            "Low": "min", "Close": "last", "Volume": "sum",
        }).dropna()
    return df


# ============================================================
#  ⑦ インジケーター計算
# ============================================================
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    c, p = df["Close"], PARAMS
    df["MA_S"]      = c.rolling(p["ma_short"]).mean()
    df["MA_L"]      = c.rolling(p["ma_long"]).mean()
    df["EMA_F"]     = c.ewm(span=p["ema_fast"],    adjust=False).mean()
    df["EMA_S"]     = c.ewm(span=p["ema_slow"],    adjust=False).mean()
    df["MACD"]      = df["EMA_F"] - df["EMA_S"]
    df["MACD_Sig"]  = df["MACD"].ewm(span=p["ema_signal"], adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Sig"]
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(p["rsi_period"]).mean()
    loss  = (-delta.clip(upper=0)).rolling(p["rsi_period"]).mean()
    df["RSI"]    = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    bb_mid       = c.rolling(p["bb_period"]).mean()
    bb_std       = c.rolling(p["bb_period"]).std()
    df["BB_Mid"] = bb_mid
    df["BB_Up"]  = bb_mid + p["bb_std"] * bb_std
    df["BB_Lo"]  = bb_mid - p["bb_std"] * bb_std
    df.dropna(inplace=True)
    return df


# ============================================================
#  ⑧ シグナル生成
# ============================================================
def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    p = PARAMS
    s = pd.Series(0.0, index=df.index)
    ma_buy  = (df["MA_S"] > df["MA_L"]) & (df["MA_S"].shift(1) <= df["MA_L"].shift(1))
    ma_sell = (df["MA_S"] < df["MA_L"]) & (df["MA_S"].shift(1) >= df["MA_L"].shift(1))
    s += ma_buy.astype(float) * 2 - ma_sell.astype(float) * 2
    s += (df["MA_S"] > df["MA_L"]).astype(float) * 0.5
    s -= (df["MA_S"] < df["MA_L"]).astype(float) * 0.5
    mc_buy  = (df["MACD"] > df["MACD_Sig"]) & (df["MACD"].shift(1) <= df["MACD_Sig"].shift(1))
    mc_sell = (df["MACD"] < df["MACD_Sig"]) & (df["MACD"].shift(1) >= df["MACD_Sig"].shift(1))
    s += mc_buy.astype(float) * 2 - mc_sell.astype(float) * 2
    rsi_buy  = df["RSI"] < p["rsi_oversell"]
    rsi_sell = df["RSI"] > p["rsi_overbuy"]
    s += rsi_buy.astype(float) * 1.5 - rsi_sell.astype(float) * 1.5
    bb_buy  = df["Close"] <= df["BB_Lo"]
    bb_sell = df["Close"] >= df["BB_Up"]
    s += bb_buy.astype(float) - bb_sell.astype(float)
    df["Score"]       = s
    df["Buy_Signal"]  = s >= p["buy_th"]
    df["Sell_Signal"] = s <= p["sell_th"]
    for col, val in [
        ("MA_Buy", ma_buy), ("MA_Sell", ma_sell),
        ("MC_Buy", mc_buy), ("MC_Sell", mc_sell),
        ("RSI_Buy", rsi_buy), ("RSI_Sell", rsi_sell),
        ("BB_Buy", bb_buy), ("BB_Sell", bb_sell),
    ]:
        df[col] = val
    return df


# ============================================================
#  ⑨ ユーティリティ
# ============================================================
def score_to_signal(score: float) -> str:
    if score >= PARAMS["buy_th"]:  return "BUY"
    if score <= PARAMS["sell_th"]: return "SELL"
    return "WAIT"

def signal_style(sig: str):
    if sig == "BUY":  return C["bright_green"], "rgba(0,230,118,0.10)",  C["bright_green"]
    if sig == "SELL": return C["bright_red"],   "rgba(255,23,68,0.10)",   C["bright_red"]
    return C["text_muted"], "rgba(30,30,30,0.4)", C["border"]


# ============================================================
#  ⑩ Discord 通知
# ============================================================
def _discord_worker(url, ticker, name, sig, price, score, tf):
    try:
        color = 0x00E676 if sig == "BUY" else 0xFF1744
        emoji = "🟢" if sig == "BUY" else "🔴"
        payload = {
            "username": "FX Analyzer",
            "embeds": [{
                "title": f"{emoji} {sig} シグナル — {name}",
                "description": f"`{ticker}`  足種: **{TIMEFRAMES[tf]['label']}**",
                "color": color,
                "fields": [
                    {"name": "💹 現在値", "value": f"`{price:.5g}`",  "inline": True},
                    {"name": "📊 スコア", "value": f"`{score:+.1f}`", "inline": True},
                    {"name": "🕐 時刻",   "value": datetime.now().strftime("%H:%M JST"), "inline": True},
                ],
                "footer": {"text": "FX Analyzer"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }
        r = requests.post(url, json=payload, timeout=8)
        status = "✓" if r.status_code in (200, 204) else f"✗{r.status_code}"
        print(f"[Discord] {status} {sig} {name}")
    except Exception as e:
        print(f"[Discord] エラー: {e}")

def send_discord(url, ticker, sig, price, score, tf):
    if not url or not url.startswith("https://discord.com/api/webhooks/"):
        return
    name = ALL_SYMBOLS.get(ticker, ticker)
    threading.Thread(target=_discord_worker,
                     args=(url, ticker, name, sig, price, score, tf),
                     daemon=True).start()


# ============================================================
#  ⑪ チャート描画
# ============================================================
def build_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    p, idx = PARAMS, df.index
    name = ALL_SYMBOLS.get(ticker, ticker)
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.02, row_heights=[0.50, 0.18, 0.16, 0.16],
        subplot_titles=[
            f"{name}  ローソク足 / MA{p['ma_short']}・{p['ma_long']} / BB",
            f"MACD ({p['ema_fast']},{p['ema_slow']},{p['ema_signal']})",
            f"RSI ({p['rsi_period']})", "シグナルスコア",
        ],
    )
    # ローソク足
    fig.add_trace(go.Candlestick(
        x=idx, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=name, showlegend=False,
        increasing_line_color=C["green"],  decreasing_line_color=C["red"],
        increasing_fillcolor=C["green"],   decreasing_fillcolor=C["red"],
    ), row=1, col=1)
    for col, lname, color, dash in [
        ("MA_S",   f"MA{p['ma_short']}", C["blue"],   "solid"),
        ("MA_L",   f"MA{p['ma_long']}",  C["orange"], "solid"),
        ("BB_Up",  "BB Upper", "rgba(150,150,150,0.6)", "dot"),
        ("BB_Lo",  "BB Lower", "rgba(150,150,150,0.6)", "dot"),
        ("BB_Mid", "BB Mid",   "rgba(120,120,120,0.4)", "dash"),
    ]:
        fill = "tonexty" if col == "BB_Lo" else None
        fc   = "rgba(150,150,150,0.04)" if col == "BB_Lo" else None
        fig.add_trace(go.Scatter(
            x=idx, y=df[col], name=lname,
            line=dict(color=color, width=1.4, dash=dash),
            fill=fill, fillcolor=fc, showlegend=(col != "BB_Mid"),
        ), row=1, col=1)
    buy_m  = df[df["Buy_Signal"]]
    sell_m = df[df["Sell_Signal"]]
    fig.add_trace(go.Scatter(
        x=buy_m.index, y=buy_m["Low"] * 0.9993, mode="markers+text", name="BUY",
        marker=dict(symbol="triangle-up",   size=12, color=C["bright_green"]),
        text=["▲"] * len(buy_m), textposition="bottom center",
        textfont=dict(size=9, color=C["bright_green"]),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sell_m.index, y=sell_m["High"] * 1.0007, mode="markers+text", name="SELL",
        marker=dict(symbol="triangle-down", size=12, color=C["bright_red"]),
        text=["▼"] * len(sell_m), textposition="top center",
        textfont=dict(size=9, color=C["bright_red"]),
    ), row=1, col=1)
    # MACD
    hc = [C["green"] if v >= 0 else C["red"] for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(x=idx, y=df["MACD_Hist"], marker_color=hc,
                         opacity=0.7, showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=idx, y=df["MACD"],    line=dict(color=C["blue"],   width=1.6), name="MACD",   showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=idx, y=df["MACD_Sig"],line=dict(color=C["orange"], width=1.6), name="Signal", showlegend=False), row=2, col=1)
    # RSI
    fig.add_trace(go.Scatter(
        x=idx, y=df["RSI"], name="RSI",
        line=dict(color="#ab47bc", width=1.8),
        fill="tozeroy", fillcolor="rgba(171,71,188,0.07)", showlegend=False,
    ), row=3, col=1)
    for yv, cc in [(p["rsi_overbuy"], C["red"]), (p["rsi_oversell"], C["green"]),
                   (50, "rgba(180,180,180,0.2)")]:
        fig.add_hline(y=yv, line_dash="dash", line_color=cc, line_width=1, row=3, col=1)
    fig.add_hrect(y0=p["rsi_overbuy"], y1=100,       fillcolor="rgba(239,83,80,0.06)",  line_width=0, row=3, col=1)
    fig.add_hrect(y0=0, y1=p["rsi_oversell"],         fillcolor="rgba(38,166,154,0.06)", line_width=0, row=3, col=1)
    # スコア
    sc = [C["bright_green"] if v >= p["buy_th"] else
          C["bright_red"]   if v <= p["sell_th"] else
          "rgba(140,140,140,0.5)" for v in df["Score"]]
    fig.add_trace(go.Bar(x=idx, y=df["Score"], marker_color=sc, opacity=0.85, showlegend=False), row=4, col=1)
    for th, cc in [(p["buy_th"], C["bright_green"]), (p["sell_th"], C["bright_red"])]:
        fig.add_hline(y=th, line_dash="dash", line_color=cc, line_width=1.2, row=4, col=1)
    fig.update_layout(
        template="plotly_dark", height=680,
        margin=dict(l=55, r=55, t=65, b=10),
        hovermode="x unified", xaxis_rangeslider_visible=False,
        paper_bgcolor=C["bg_base"], plot_bgcolor=C["bg_base"],
        font=dict(size=11, color="#c9d1d9"),
        legend=dict(orientation="h", y=1.03, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        hoverlabel=dict(bgcolor=C["bg_panel"], font_size=12),
    )
    fig.update_yaxes(gridcolor="rgba(48,54,61,0.8)", zerolinecolor="rgba(48,54,61,0.6)")
    for r in [1, 2, 3]:
        fig.update_xaxes(gridcolor="rgba(48,54,61,0.4)", showticklabels=False, row=r, col=1)
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=10, color=C["text_muted"])
    return fig


# ============================================================
#  ⑫ Dashアプリ
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap",
    ],
    title="FX Analyzer",
    suppress_callback_exceptions=True,
    update_title=None,
)


# ============================================================
#  ⑬ サイドバー（INSTRUMENTS定義順で生成）
# ============================================================
def make_sidebar():
    items = []
    for cat, syms in INSTRUMENTS.items():
        items.append(html.Div(cat, style={
            "fontSize": "10px", "fontWeight": "700",
            "color": C["text_muted"], "textTransform": "uppercase",
            "padding": "10px 10px 4px", "letterSpacing": "0.8px",
        }))
        for ticker, label in syms.items():
            is_active = (ticker == DEFAULT_SYMBOL)
            items.append(html.Button(
                label,
                id={"type": "sym-btn", "index": ticker},
                n_clicks=0,
                style=CSS["sym_btn_active"] if is_active else CSS["sym_btn"],
            ))
    return html.Div(items, style={
        "width": "170px", "flexShrink": "0",
        "background": C["bg_panel"],
        "borderRight": f"1px solid {C['border']}",
        "height": "100vh", "overflowY": "auto",
        "position": "sticky", "top": "0",
        "paddingBottom": "20px",
    })


def make_tf_buttons():
    return [
        dbc.Button(
            v["label"],
            id={"type": "tf-btn", "index": k},
            n_clicks=0, size="sm",
            color="primary" if k == DEFAULT_TF else "secondary",
            outline=(k != DEFAULT_TF),
            className="me-1",
            style={"fontSize": "11px", "minWidth": "52px", "padding": "3px 8px"},
        )
        for k, v in TIMEFRAMES.items()
    ]


app.layout = html.Div(
    style={"background": C["bg_base"], "minHeight": "100vh",
           "fontFamily": "'Noto Sans JP', sans-serif",
           "display": "flex", "flexDirection": "column"},
    children=[
        # ヘッダー
        html.Div(style={
            "background": C["bg_panel"], "borderBottom": f"1px solid {C['border']}",
            "padding": "8px 18px", "display": "flex",
            "alignItems": "center", "justifyContent": "space-between", "flexShrink": "0",
        }, children=[
            html.Div([
                html.Span("📊 ", style={"fontSize": "18px"}),
                html.Span("FX / 先物 / コモディティ アナライザー",
                          style={"fontSize": "16px", "fontWeight": "700", "color": C["text_main"]}),
            ]),
            html.Div(id="header-status", style={"fontSize": "11px", "color": C["text_muted"]}),
        ]),

        # ボディ
        html.Div(style={"display": "flex", "flex": "1", "overflow": "hidden"}, children=[

            # サイドバー
            make_sidebar(),

            # メインエリア
            html.Div(style={"flex": "1", "overflow": "auto", "padding": "12px 16px"}, children=[

                # ツールバー
                html.Div(style={
                    "display": "flex", "alignItems": "center",
                    "gap": "10px", "marginBottom": "12px", "flexWrap": "wrap",
                }, children=[
                    html.Div([
                        html.Span("足種：", style={"fontSize": "11px", "color": C["text_muted"], "marginRight": "6px"}),
                        *make_tf_buttons(),
                    ], style={"display": "flex", "alignItems": "center"}),
                    dbc.Button("🔄 更新", id="refresh-btn", n_clicks=0,
                               size="sm", color="light", outline=True,
                               style={"fontSize": "11px"}),
                    dcc.Loading(
                        html.Div(id="loading-msg",
                                 style={"fontSize": "11px", "color": C["text_muted"]}),
                        type="circle", color=C["blue"],
                    ),
                    html.Div(style={"marginLeft": "auto"}, children=[
                        dbc.Button("⚙ 設定", id="settings-toggle", n_clicks=0,
                                   size="sm", color="secondary", outline=True,
                                   style={"fontSize": "11px"}),
                    ]),
                ]),

                # 設定パネル
                dbc.Collapse(id="settings-panel", is_open=False, children=[
                    html.Div(style={
                        "background": C["bg_panel"], "border": f"1px solid {C['border']}",
                        "borderRadius": "8px", "padding": "14px 16px", "marginBottom": "12px",
                    }, children=[
                        html.Div("Discord Webhook 設定",
                                 style={"fontSize": "12px", "fontWeight": "700",
                                        "color": C["text_main"], "marginBottom": "10px"}),
                        html.Div(style={"display": "flex", "gap": "10px", "alignItems": "center"}, children=[
                            dcc.Input(
                                id="webhook-input", type="text",
                                placeholder="https://discord.com/api/webhooks/XXXXXX/YYYYYY",
                                value=DISCORD_WEBHOOK_URL, debounce=True,
                                style={
                                    "flex": "1", "background": "#0d1117",
                                    "border": f"1px solid {C['border']}",
                                    "borderRadius": "6px", "padding": "6px 10px",
                                    "color": C["text_main"], "fontSize": "12px", "outline": "none",
                                },
                            ),
                            dbc.Button("テスト送信", id="test-discord-btn", n_clicks=0,
                                       size="sm", color="primary",
                                       style={"fontSize": "11px", "whiteSpace": "nowrap"}),
                        ]),
                        html.Div(id="discord-status",
                                 style={"fontSize": "11px", "color": C["text_muted"], "marginTop": "6px"}),
                        html.Div([
                            html.Span("通知タイミング: ", style={"fontSize": "11px", "color": C["text_muted"]}),
                            html.Span("WAIT→BUY または WAIT/BUY→SELL に変化したとき",
                                      style={"fontSize": "11px", "color": C["text_main"]}),
                        ], style={"marginTop": "8px"}),
                    ]),
                ]),

                # シグナル + 統計カード
                html.Div(style={
                    "display": "grid", "gridTemplateColumns": "200px 1fr",
                    "gap": "10px", "marginBottom": "10px",
                }, children=[
                    html.Div(id="signal-card", style={
                        "borderRadius": "8px", "border": f"1px solid {C['border']}",
                        "background": C["bg_panel"], "padding": "14px",
                        "display": "flex", "flexDirection": "column",
                        "alignItems": "center", "justifyContent": "center",
                        "minHeight": "115px",
                    }),
                    html.Div(style={
                        "display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "8px",
                    }, children=[
                        html.Div(id="stat-price", style=CSS["stat_card"]),
                        html.Div(id="stat-rsi",   style=CSS["stat_card"]),
                        html.Div(id="stat-macd",  style=CSS["stat_card"]),
                        html.Div(id="stat-score", style=CSS["stat_card"]),
                    ]),
                ]),

                # インジケーターバッジ
                html.Div(id="ind-badges",
                         style={"display": "flex", "flexWrap": "wrap",
                                "gap": "4px", "marginBottom": "10px"}),

                # チャート
                dcc.Graph(
                    id="main-chart",
                    config={
                        "scrollZoom": True, "displayModeBar": True,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "modeBarButtonsToAdd": ["drawline", "eraseshape"],
                        "toImageButtonOptions": {"filename": "fx_chart"},
                    },
                    style={"borderRadius": "8px", "overflow": "hidden",
                           "border": f"1px solid {C['border']}"},
                ),

                # シグナル履歴
                html.Div(style={"marginTop": "12px"}, children=[
                    html.Div("直近シグナル履歴",
                             style={"fontSize": "11px", "color": C["text_muted"], "marginBottom": "6px"}),
                    html.Div(id="sig-history"),
                ]),
            ]),
        ]),

        # Store / Interval
        dcc.Store(id="tf-store",      data=DEFAULT_TF),
        dcc.Store(id="symbol-store",  data=DEFAULT_SYMBOL),
        dcc.Store(id="signal-store",  data={}),
        dcc.Store(id="webhook-store", data=DISCORD_WEBHOOK_URL),
        dcc.Interval(id="auto-interval", interval=REFRESH_MS, n_intervals=0),
    ],
)


# ============================================================
#  ⑭ コールバック: 設定パネル開閉
# ============================================================
@app.callback(
    Output("settings-panel", "is_open"),
    Input("settings-toggle", "n_clicks"),
    State("settings-panel", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings(n, is_open):
    return not is_open


# ============================================================
#  ⑮ コールバック: Webhook URL → Store
# ============================================================
@app.callback(
    Output("webhook-store", "data"),
    Input("webhook-input", "value"),
    prevent_initial_call=True,
)
def save_webhook(url):
    return url or ""


# ============================================================
#  ⑯ コールバック: Discord テスト送信
# ============================================================
@app.callback(
    Output("discord-status", "children"),
    Output("discord-status", "style"),
    Input("test-discord-btn", "n_clicks"),
    State("webhook-store", "data"),
    prevent_initial_call=True,
)
def test_discord(n, url):
    if not url or not url.startswith("https://discord.com/api/webhooks/"):
        return "⚠ 有効なWebhook URLを入力してください", {"fontSize": "11px", "color": C["red"]}
    try:
        r = requests.post(url, json={
            "username": "FX Analyzer",
            "content": "✅ **テスト通知** — FX Analyzerとの接続成功！",
        }, timeout=8)
        if r.status_code in (200, 204):
            return "✅ 送信成功！Discordを確認してください", {"fontSize": "11px", "color": C["bright_green"]}
        return f"❌ 送信失敗: {r.status_code}", {"fontSize": "11px", "color": C["red"]}
    except Exception as e:
        return f"❌ エラー: {str(e)[:60]}", {"fontSize": "11px", "color": C["red"]}


# ============================================================
#  ⑰ コールバック: 銘柄選択 → symbol-store
#  【修正】ALL パターンマッチングを使用
# ============================================================
@app.callback(
    Output("symbol-store", "data"),
    Input({"type": "sym-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_symbol(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    # どれかが None や 0 以外のクリックを持つものを特定
    triggered = ctx.triggered[0]
    if triggered["value"] is None or triggered["value"] == 0:
        return dash.no_update
    try:
        prop_id = triggered["prop_id"]          # 例: '{"index":"EURUSD=X","type":"sym-btn"}.n_clicks'
        id_part = prop_id.rsplit(".", 1)[0]     # JSON部分だけ取り出す
        return json.loads(id_part)["index"]
    except Exception:
        return dash.no_update


# ============================================================
#  ⑱ コールバック: サイドバーボタンのアクティブスタイル
#  【修正】ALL パターンマッチングで INSTRUMENTS 定義順に対応
# ============================================================
@app.callback(
    Output({"type": "sym-btn", "index": ALL}, "style"),
    Input("symbol-store", "data"),
)
def update_sym_styles(active):
    # SIDEBAR_ORDER = INSTRUMENTS定義順 → サイドバー生成順と一致
    return [
        CSS["sym_btn_active"] if ticker == active else CSS["sym_btn"]
        for ticker in SIDEBAR_ORDER
    ]


# ============================================================
#  ⑲ コールバック: 足種ボタン → tf-store
# ============================================================
@app.callback(
    Output("tf-store", "data"),
    Input({"type": "tf-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_tf(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    triggered = ctx.triggered[0]
    if triggered["value"] is None or triggered["value"] == 0:
        return dash.no_update
    try:
        id_part = triggered["prop_id"].rsplit(".", 1)[0]
        return json.loads(id_part)["index"]
    except Exception:
        return dash.no_update


# ============================================================
#  ⑳ コールバック: 足種ボタンのスタイル
# ============================================================
@app.callback(
    [Output({"type": "tf-btn", "index": k}, "color")   for k in TIMEFRAMES] +
    [Output({"type": "tf-btn", "index": k}, "outline") for k in TIMEFRAMES],
    Input("tf-store", "data"),
)
def update_tf_styles(active):
    colors   = ["primary" if k == active else "secondary" for k in TIMEFRAMES]
    outlines = [False      if k == active else True        for k in TIMEFRAMES]
    return colors + outlines


# ============================================================
#  ㉑ コールバック: メイン更新
# ============================================================
@app.callback(
    Output("main-chart",    "figure"),
    Output("signal-card",   "children"),
    Output("signal-card",   "style"),
    Output("stat-price",    "children"),
    Output("stat-rsi",      "children"),
    Output("stat-macd",     "children"),
    Output("stat-score",    "children"),
    Output("ind-badges",    "children"),
    Output("sig-history",   "children"),
    Output("header-status", "children"),
    Output("loading-msg",   "children"),
    Output("signal-store",  "data"),
    Input("auto-interval",  "n_intervals"),
    Input("refresh-btn",    "n_clicks"),
    Input("symbol-store",   "data"),
    Input("tf-store",       "data"),
    State("signal-store",   "data"),
    State("webhook-store",  "data"),
)
def refresh_all(n_int, n_btn, ticker, tf_key, prev_signals, webhook_url):
    ticker      = ticker   or DEFAULT_SYMBOL
    tf_key      = tf_key   or DEFAULT_TF
    name        = ALL_SYMBOLS.get(ticker, ticker)
    now_str     = datetime.now().strftime("%H:%M:%S")
    prev_signals = prev_signals or {}

    # データ取得
    try:
        df = fetch_ohlcv(ticker, tf_key)
        if df.empty:
            raise ValueError("データ取得失敗（Yahoo Finance）")
        df = add_indicators(df)
        df = add_signals(df)
    except Exception as e:
        empty = go.Figure()
        empty.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg_base"],
            annotations=[dict(text=f"エラー: {e}", xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False,
                              font=dict(size=13, color=C["red"]))],
        )
        return (empty, f"⚠ {e}", {}, "", "", "", "", "", "", "", "", prev_signals)

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    score  = float(latest["Score"])
    sig    = score_to_signal(score)
    sig_color, sig_bg, sig_border = signal_style(sig)

    # Discord通知（シグナル変化時のみ）
    sig_key  = f"{ticker}_{tf_key}"
    prev_sig = prev_signals.get(sig_key, "WAIT")
    if sig != prev_sig and sig != "WAIT":
        send_discord(
            webhook_url or DISCORD_WEBHOOK_URL,
            ticker, sig, float(latest["Close"]), score, tf_key,
        )
    new_signals = {**prev_signals, sig_key: sig}

    # チャート
    fig = build_chart(df, ticker)

    # シグナルカード
    pdiff = float(latest["Close"]) - float(prev["Close"])
    sig_icon = {"BUY": "🟢", "SELL": "🔴", "WAIT": "⚪"}[sig]
    signal_children = [
        html.Div(f"{sig_icon} {sig}", style={
            "fontSize": "30px", "fontWeight": "900",
            "color": sig_color, "lineHeight": "1", "letterSpacing": "2px",
        }),
        html.Div(name, style={"fontSize": "11px", "color": C["text_muted"], "marginTop": "4px"}),
        html.Div(f"スコア: {score:+.1f}",
                 style={"fontSize": "12px", "color": sig_color, "marginTop": "4px"}),
        html.Div(
            f"{'▲' if pdiff >= 0 else '▼'} {abs(pdiff):.4g}",
            style={"fontSize": "11px",
                   "color": C["green"] if pdiff >= 0 else C["red"],
                   "marginTop": "5px"},
        ),
    ]
    card_style = {
        "borderRadius": "8px", "border": f"1px solid {sig_border}",
        "background": sig_bg, "padding": "14px",
        "display": "flex", "flexDirection": "column",
        "alignItems": "center", "justifyContent": "center",
        "minHeight": "115px", "boxShadow": f"0 0 14px {sig_bg}",
    }

    # 統計カード
    def stat(label, value, sub="", vc=C["text_main"]):
        return [
            html.Div(label, style=CSS["stat_label"]),
            html.Div(value, style={**CSS["stat_value"], "color": vc}),
            html.Div(sub,   style=CSS["stat_sub"]),
        ]

    cv   = float(latest["Close"])
    rsi  = float(latest["RSI"])
    macd = float(latest["MACD"])
    msig = float(latest["MACD_Sig"])
    rsi_c  = C["red"] if rsi > 70 else C["green"] if rsi < 30 else C["text_main"]
    macd_c = C["green"] if macd > msig else C["red"]

    s_price = stat("現在値", f"{cv:.5g}",    f"MA{PARAMS['ma_short']}: {float(latest['MA_S']):.5g}")
    s_rsi   = stat("RSI",   f"{rsi:.1f}",   "OB >70 / OS <30", rsi_c)
    s_macd  = stat("MACD",  f"{macd:+.4g}", f"Sig: {msig:+.4g}", macd_c)
    s_score = stat("スコア", f"{score:+.1f}",
                   f"Buy≥{PARAMS['buy_th']} / Sell≤{PARAMS['sell_th']}", sig_color)

    # バッジ
    def badge(active, label):
        color = C["bright_green"] if active else "rgba(100,100,100,0.35)"
        bg    = "rgba(0,230,118,0.10)" if active else "rgba(25,25,25,0.5)"
        return html.Span(label, style={
            "color": color, "background": bg,
            "border": f"1px solid {color}", "borderRadius": "4px",
            "padding": "2px 7px", "fontSize": "10px", "whiteSpace": "nowrap",
        })

    badges = [
        badge(bool(latest["MA_Buy"]),   "✓ MAゴールデンクロス"),
        badge(bool(latest["MA_Sell"]),  "✗ MAデッドクロス"),
        badge(bool(latest["MC_Buy"]),   "✓ MACDクロス(買)"),
        badge(bool(latest["MC_Sell"]),  "✗ MACDクロス(売)"),
        badge(bool(latest["RSI_Buy"]),  f"✓ RSI過売り(<{PARAMS['rsi_oversell']})"),
        badge(bool(latest["RSI_Sell"]), f"✗ RSI過買い(>{PARAMS['rsi_overbuy']})"),
        badge(bool(latest["BB_Buy"]),   "✓ BB下限タッチ"),
        badge(bool(latest["BB_Sell"]),  "✗ BB上限タッチ"),
    ]

    # 履歴
    combined = pd.concat([
        df[df["Buy_Signal"]].assign(_t="BUY"),
        df[df["Sell_Signal"]].assign(_t="SELL"),
    ]).sort_index(ascending=False).head(8)
    history_rows = []
    for dt, row in combined.iterrows():
        t = row["_t"]
        c = C["bright_green"] if t == "BUY" else C["bright_red"]
        history_rows.append(html.Div(style=CSS["hist_row"], children=[
            html.Span(t,             style={"color": c, "fontWeight": "700", "minWidth": "34px"}),
            html.Span(str(dt)[:16],  style={"color": C["text_muted"], "minWidth": "105px"}),
            html.Span(f"{float(row['Close']):.5g}", style={"minWidth": "80px"}),
            html.Span(f"スコア {float(row['Score']):+.1f}", style={"color": c}),
        ]))
    if not history_rows:
        history_rows = [html.Div("シグナルなし",
                                 style={"color": C["text_muted"], "fontSize": "11px"})]

    # ヘッダー
    discord_dot = "🔔" if (webhook_url or DISCORD_WEBHOOK_URL) else "🔕"
    header = [
        html.Span(f"📍 {name} ({ticker})", style={"marginRight": "14px", "color": C["text_main"]}),
        html.Span(f"足種: {TIMEFRAMES[tf_key]['label']}", style={"marginRight": "14px"}),
        html.Span(f"更新: {now_str}", style={"marginRight": "14px"}),
        html.Span(f"{discord_dot} Discord"),
    ]
    loading_msg = html.Span(
        f"✓ {now_str}  {len(df)}本",
        style={"color": C["green"], "fontSize": "11px"},
    )

    return (
        fig, signal_children, card_style,
        s_price, s_rsi, s_macd, s_score,
        badges, history_rows, header, loading_msg, new_signals,
    )


# ============================================================
#  起動
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  FX / 先物 / コモディティ アナライザー")
    print(f"  http://localhost:{PORT}")
    print(f"  Discord: {'有効' if DISCORD_WEBHOOK_URL else 'UI設定パネルで入力'}")
    print("  停止: Ctrl+C")
    print("=" * 55)
    app.run(debug=False, host="0.0.0.0", port=PORT)
