"""
USDJPY FX トレード分析 Webアプリ
=====================================
常時稼働型・足種切り替え対応・1分自動更新

ライブラリのインストール:
    pip install dash dash-bootstrap-components yfinance pandas numpy plotly

起動:
    python usdjpy_webapp.py

アクセス:
    http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, clientside_callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


# ============================================================
#  設定
# ============================================================
TICKER = "USDJPY=X"

# 足種プリセット
TIMEFRAMES = {
    "15m":  {"label": "15分", "interval": "15m",  "period": "5d"},
    "1h":   {"label": "1時間", "interval": "1h",   "period": "60d"},
    "4h":   {"label": "4時間", "interval": "1h",   "period": "60d"},   # 後処理でリサンプル
    "1d":   {"label": "日足",  "interval": "1d",   "period": "6mo"},
    "1wk":  {"label": "週足",  "interval": "1wk",  "period": "2y"},
}
DEFAULT_TF = "1h"

# インジケーターパラメーター
PARAMS = {
    "ma_short":      20,
    "ma_long":       50,
    "ema_fast":      12,
    "ema_slow":      26,
    "ema_signal":    9,
    "rsi_period":    14,
    "rsi_overbuy":   70,
    "rsi_oversell":  30,
    "bb_period":     20,
    "bb_std":        2.0,
    "buy_th":        2.0,
    "sell_th":       -2.0,
}

# インラインスタイル定数（html.Style の代わり）
CSS = {
    "stat_card": {
        "background": "#161b22",
        "border": "1px solid #30363d",
        "borderRadius": "10px",
        "padding": "12px 14px",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
    },
    "stat_label": {
        "fontSize": "11px",
        "color": "#8b949e",
        "marginBottom": "4px",
    },
    "stat_value": {
        "fontSize": "22px",
        "fontWeight": "700",
        "color": "#e6edf3",
        "lineHeight": "1",
    },
    "stat_sub": {
        "fontSize": "10px",
        "color": "#8b949e",
        "marginTop": "3px",
    },
    "hist_row": {
        "display": "flex",
        "alignItems": "center",
        "gap": "12px",
        "padding": "6px 12px",
        "background": "#161b22",
        "border": "1px solid #21262d",
        "borderRadius": "6px",
        "marginBottom": "4px",
        "fontSize": "12px",
        "color": "#c9d1d9",
    },
}

REFRESH_MS = 60_000   # 1分ごとに自動更新


# ============================================================
#  データ取得
# ============================================================
def fetch_ohlcv(tf_key: str) -> pd.DataFrame:
    cfg = TIMEFRAMES[tf_key]
    df = yf.download(
        TICKER,
        period=cfg["period"],
        interval=cfg["interval"],
        progress=False,
        auto_adjust=True,
    )
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.dropna(inplace=True)

    # 4時間足: 1h データを4本リサンプル
    if tf_key == "4h":
        df = df.resample("4h").agg({
            "Open": "first", "High": "max",
            "Low": "min",    "Close": "last",
            "Volume": "sum",
        }).dropna()

    return df


# ============================================================
#  テクニカルインジケーター
# ============================================================
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    c = df["Close"]
    p = PARAMS

    df["MA_S"]     = c.rolling(p["ma_short"]).mean()
    df["MA_L"]     = c.rolling(p["ma_long"]).mean()
    df["EMA_F"]    = c.ewm(span=p["ema_fast"],   adjust=False).mean()
    df["EMA_S"]    = c.ewm(span=p["ema_slow"],   adjust=False).mean()
    df["MACD"]     = df["EMA_F"] - df["EMA_S"]
    df["MACD_Sig"] = df["MACD"].ewm(span=p["ema_signal"], adjust=False).mean()
    df["MACD_Hist"]= df["MACD"] - df["MACD_Sig"]

    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(p["rsi_period"]).mean()
    loss  = (-delta.clip(upper=0)).rolling(p["rsi_period"]).mean()
    df["RSI"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

    bb_mid     = c.rolling(p["bb_period"]).mean()
    bb_std     = c.rolling(p["bb_period"]).std()
    df["BB_Mid"]= bb_mid
    df["BB_Up"] = bb_mid + p["bb_std"] * bb_std
    df["BB_Lo"] = bb_mid - p["bb_std"] * bb_std

    df.dropna(inplace=True)
    return df


# ============================================================
#  シグナル生成（スコアリング方式）
# ============================================================
def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    p = PARAMS
    score = pd.Series(0.0, index=df.index)

    # ① MA ゴールデン/デッドクロス (+2/-2) + トレンド (+0.5/-0.5)
    ma_buy  = (df["MA_S"] > df["MA_L"]) & (df["MA_S"].shift(1) <= df["MA_L"].shift(1))
    ma_sell = (df["MA_S"] < df["MA_L"]) & (df["MA_S"].shift(1) >= df["MA_L"].shift(1))
    score  += ma_buy.astype(float) * 2 - ma_sell.astype(float) * 2
    score  += (df["MA_S"] > df["MA_L"]).astype(float) * 0.5
    score  -= (df["MA_S"] < df["MA_L"]).astype(float) * 0.5

    # ② MACD クロス (+2/-2)
    mc_buy  = (df["MACD"] > df["MACD_Sig"]) & (df["MACD"].shift(1) <= df["MACD_Sig"].shift(1))
    mc_sell = (df["MACD"] < df["MACD_Sig"]) & (df["MACD"].shift(1) >= df["MACD_Sig"].shift(1))
    score  += mc_buy.astype(float) * 2 - mc_sell.astype(float) * 2

    # ③ RSI (+1.5/-1.5)
    rsi_buy  = df["RSI"] < p["rsi_oversell"]
    rsi_sell = df["RSI"] > p["rsi_overbuy"]
    score   += rsi_buy.astype(float) * 1.5 - rsi_sell.astype(float) * 1.5

    # ④ BB タッチ (+1/-1)
    bb_buy  = df["Close"] <= df["BB_Lo"]
    bb_sell = df["Close"] >= df["BB_Up"]
    score  += bb_buy.astype(float) - bb_sell.astype(float)

    df["Score"]       = score
    df["Buy_Signal"]  = score >= p["buy_th"]
    df["Sell_Signal"] = score <= p["sell_th"]
    df["MA_Buy"]      = ma_buy
    df["MA_Sell"]     = ma_sell
    df["MC_Buy"]      = mc_buy
    df["MC_Sell"]     = mc_sell
    df["RSI_Buy"]     = rsi_buy
    df["RSI_Sell"]    = rsi_sell
    df["BB_Buy"]      = bb_buy
    df["BB_Sell"]     = bb_sell
    return df


# ============================================================
#  チャート描画
# ============================================================
def build_chart(df: pd.DataFrame, tf_key: str) -> go.Figure:
    p = PARAMS
    idx = df.index

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.50, 0.18, 0.16, 0.16],
        subplot_titles=[
            f"USDJPY  ローソク足 / MA{p['ma_short']}・{p['ma_long']} / Bollinger Bands",
            f"MACD ({p['ema_fast']},{p['ema_slow']},{p['ema_signal']})",
            f"RSI ({p['rsi_period']})",
            "シグナルスコア",
        ],
    )

    # ── 1段目: ローソク足 ──────────────────────
    fig.add_trace(go.Candlestick(
        x=idx, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="USDJPY",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        increasing_fillcolor="#26a69a",
        decreasing_fillcolor="#ef5350",
        showlegend=False,
    ), row=1, col=1)

    for col, name, color, dash in [
        ("MA_S",   f"MA{p['ma_short']}", "#42a5f5", "solid"),
        ("MA_L",   f"MA{p['ma_long']}",  "#ffa726", "solid"),
        ("BB_Up",  "BB Upper",           "rgba(160,160,160,0.6)", "dot"),
        ("BB_Lo",  "BB Lower",           "rgba(160,160,160,0.6)", "dot"),
        ("BB_Mid", "BB Mid",             "rgba(130,130,130,0.4)", "dash"),
    ]:
        fill = "tonexty" if col == "BB_Lo" else None
        fc   = "rgba(160,160,160,0.05)" if col == "BB_Lo" else None
        fig.add_trace(go.Scatter(
            x=idx, y=df[col], name=name,
            line=dict(color=color, width=1.4, dash=dash),
            fill=fill, fillcolor=fc,
            showlegend=(col not in ("BB_Mid",)),
        ), row=1, col=1)

    # 買い/売りマーカー
    buy_df  = df[df["Buy_Signal"]]
    sell_df = df[df["Sell_Signal"]]
    fig.add_trace(go.Scatter(
        x=buy_df.index, y=buy_df["Low"] * 0.9993,
        mode="markers+text", name="買いシグナル",
        marker=dict(symbol="triangle-up", size=13, color="#00e676",
                    line=dict(color="#004d26", width=1)),
        text=["▲BUY"] * len(buy_df),
        textposition="bottom center",
        textfont=dict(size=9, color="#00e676"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sell_df.index, y=sell_df["High"] * 1.0007,
        mode="markers+text", name="売りシグナル",
        marker=dict(symbol="triangle-down", size=13, color="#ff1744",
                    line=dict(color="#7f0000", width=1)),
        text=["▼SELL"] * len(sell_df),
        textposition="top center",
        textfont=dict(size=9, color="#ff1744"),
    ), row=1, col=1)

    # ── 2段目: MACD ──────────────────────────
    hist_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["MACD_Hist"]]
    fig.add_trace(go.Bar(
        x=idx, y=df["MACD_Hist"], name="MACD Hist",
        marker_color=hist_colors, opacity=0.7, showlegend=False,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["MACD"], name="MACD",
        line=dict(color="#42a5f5", width=1.6), showlegend=False,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=idx, y=df["MACD_Sig"], name="Signal",
        line=dict(color="#ffa726", width=1.6), showlegend=False,
    ), row=2, col=1)

    # ── 3段目: RSI ───────────────────────────
    fig.add_trace(go.Scatter(
        x=idx, y=df["RSI"], name="RSI",
        line=dict(color="#ab47bc", width=1.8),
        fill="tozeroy", fillcolor="rgba(171,71,188,0.07)",
        showlegend=False,
    ), row=3, col=1)
    for y_val, color in [(p["rsi_overbuy"], "#ef5350"), (p["rsi_oversell"], "#26a69a"), (50, "rgba(180,180,180,0.25)")]:
        fig.add_hline(y=y_val, line_dash="dash", line_color=color, line_width=1, row=3, col=1)
    fig.add_hrect(y0=p["rsi_overbuy"], y1=100,
                  fillcolor="rgba(239,83,80,0.07)", line_width=0, row=3, col=1)
    fig.add_hrect(y0=0, y1=p["rsi_oversell"],
                  fillcolor="rgba(38,166,154,0.07)", line_width=0, row=3, col=1)

    # ── 4段目: スコア ────────────────────────
    score_colors = [
        "#00e676" if v >= p["buy_th"] else
        "#ff1744" if v <= p["sell_th"] else
        "rgba(150,150,150,0.55)"
        for v in df["Score"]
    ]
    fig.add_trace(go.Bar(
        x=idx, y=df["Score"], name="スコア",
        marker_color=score_colors, opacity=0.85, showlegend=False,
    ), row=4, col=1)
    for th, color in [(p["buy_th"], "#00e676"), (p["sell_th"], "#ff1744")]:
        fig.add_hline(y=th, line_dash="dash", line_color=color, line_width=1.2, row=4, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=700,
        margin=dict(l=55, r=55, t=70, b=10),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(family="'Noto Sans JP', sans-serif", size=11, color="#c9d1d9"),
        legend=dict(
            orientation="h", y=1.03, x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
        ),
        hoverlabel=dict(bgcolor="#161b22", font_size=12),
    )
    fig.update_yaxes(gridcolor="rgba(48,54,61,0.8)", zerolinecolor="rgba(48,54,61,0.8)")
    fig.update_xaxes(gridcolor="rgba(48,54,61,0.5)", showticklabels=False, row=1, col=1)
    fig.update_xaxes(gridcolor="rgba(48,54,61,0.5)", showticklabels=False, row=2, col=1)
    fig.update_xaxes(gridcolor="rgba(48,54,61,0.5)", showticklabels=False, row=3, col=1)
    fig.update_yaxes(title_text="JPY", row=1, col=1, title_font_size=10)
    fig.update_yaxes(range=[0, 100], row=3, col=1)

    # サブタイトル文字色
    for ann in fig["layout"]["annotations"]:
        ann["font"] = dict(size=11, color="#8b949e")

    return fig


# ============================================================
#  ユーティリティ
# ============================================================
def signal_label(score: float) -> tuple[str, str, str]:
    """(label, color, bg_color)"""
    p = PARAMS
    if score >= p["buy_th"]:
        return "BUY", "#00e676", "rgba(0,230,118,0.12)"
    if score <= p["sell_th"]:
        return "SELL", "#ff1744", "rgba(255,23,68,0.12)"
    return "WAIT", "#90a4ae", "rgba(144,164,174,0.10)"

def ind_badge(active: bool, label: str) -> html.Span:
    color = "#00e676" if active else "rgba(100,100,100,0.4)"
    bg    = "rgba(0,230,118,0.12)" if active else "rgba(30,30,30,0.5)"
    return html.Span(label, style={
        "color": color, "background": bg,
        "border": f"1px solid {color}",
        "borderRadius": "4px", "padding": "2px 7px",
        "fontSize": "11px", "marginRight": "4px", "whiteSpace": "nowrap",
    })


# ============================================================
#  アプリ初期化
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap",
    ],
    title="USDJPY FX Analyzer",
    suppress_callback_exceptions=True,
    update_title=None,
)

# ============================================================
#  レイアウト
# ============================================================
def tf_button(key: str, active: bool) -> dbc.Button:
    return dbc.Button(
        TIMEFRAMES[key]["label"],
        id={"type": "tf-btn", "index": key},
        n_clicks=0,
        size="sm",
        color="primary" if active else "secondary",
        outline=not active,
        className="me-1",
        style={"fontSize": "12px", "minWidth": "56px"},
    )

app.layout = html.Div(
    style={"background": "#0d1117", "minHeight": "100vh", "fontFamily": "'Noto Sans JP', sans-serif"},
    children=[
        # ─── ヘッダー ───────────────────────────────────────────
        html.Div(style={
            "background": "#161b22", "borderBottom": "1px solid #30363d",
            "padding": "10px 20px", "display": "flex",
            "alignItems": "center", "justifyContent": "space-between",
        }, children=[
            html.Div([
                html.Span("📊", style={"fontSize": "20px", "marginRight": "8px"}),
                html.Span("USDJPY FX Analyzer",
                          style={"fontSize": "18px", "fontWeight": "700", "color": "#e6edf3"}),
            ]),
            html.Div(id="header-status", style={"fontSize": "12px", "color": "#8b949e"}),
        ]),

        # ─── メインコンテンツ ────────────────────────────────────
        html.Div(style={"padding": "14px 20px"}, children=[

            # 足種切り替え + コントロール行
            html.Div(style={
                "display": "flex", "alignItems": "center",
                "marginBottom": "14px", "gap": "12px",
            }, children=[
                html.Div([
                    html.Span("足種：", style={"fontSize": "12px", "color": "#8b949e", "marginRight": "8px"}),
                    *[tf_button(k, k == DEFAULT_TF) for k in TIMEFRAMES],
                ], style={"display": "flex", "alignItems": "center"}),
                dbc.Button(
                    ["🔄 更新"],
                    id="refresh-btn", n_clicks=0, size="sm",
                    color="light", outline=True,
                    style={"fontSize": "12px"},
                ),
                dcc.Loading(
                    html.Div(id="loading-indicator", style={"fontSize": "12px", "color": "#8b949e"}),
                    type="circle", color="#42a5f5",
                ),
            ]),

            # シグナル + 統計カード行
            html.Div(style={
                "display": "grid",
                "gridTemplateColumns": "220px 1fr",
                "gap": "12px", "marginBottom": "14px",
            }, children=[

                # シグナルカード
                html.Div(id="signal-card", style={
                    "borderRadius": "10px", "border": "1px solid #30363d",
                    "background": "#161b22", "padding": "16px",
                    "display": "flex", "flexDirection": "column",
                    "alignItems": "center", "justifyContent": "center",
                    "minHeight": "130px",
                }),

                # 統計カード
                html.Div(style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "10px",
                }, children=[
                    html.Div(id="stat-price",  style=CSS["stat_card"]),
                    html.Div(id="stat-rsi",    style=CSS["stat_card"]),
                    html.Div(id="stat-macd",   style=CSS["stat_card"]),
                    html.Div(id="stat-score",  style=CSS["stat_card"]),
                ]),
            ]),

            # インジケーター内訳バッジ行
            html.Div(id="indicator-badges", style={
                "marginBottom": "12px", "display": "flex", "flexWrap": "wrap", "gap": "4px",
            }),

            # チャート
            dcc.Graph(
                id="main-chart",
                config={
                    "scrollZoom": True,
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "modeBarButtonsToAdd": ["drawline", "eraseshape"],
                    "toImageButtonOptions": {"filename": "USDJPY_chart"},
                },
                style={"borderRadius": "10px", "overflow": "hidden",
                       "border": "1px solid #30363d"},
            ),

            # 直近シグナル履歴
            html.Div(style={"marginTop": "14px"}, children=[
                html.Div("直近シグナル履歴",
                         style={"fontSize": "12px", "color": "#8b949e", "marginBottom": "6px"}),
                html.Div(id="signal-history"),
            ]),
        ]),

        # ─── State / Timer ──────────────────────────────────────
        dcc.Store(id="tf-store", data=DEFAULT_TF),
        dcc.Interval(id="auto-interval", interval=REFRESH_MS, n_intervals=0),

    ],
)


# ============================================================
#  コールバック: 足種ボタン → Store に保存
# ============================================================
@app.callback(
    Output("tf-store", "data"),
    [Input({"type": "tf-btn", "index": k}, "n_clicks") for k in TIMEFRAMES],
    prevent_initial_call=True,
)
def update_tf(*n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return DEFAULT_TF
    triggered_id = ctx.triggered[0]["prop_id"]
    # {"type":"tf-btn","index":"1h"}.n_clicks → "1h"
    import json
    key_str = triggered_id.split(".")[0]
    try:
        key = json.loads(key_str)["index"]
    except Exception:
        return DEFAULT_TF
    return key


# ============================================================
#  コールバック: 足種ボタンのアクティブ状態を更新
# ============================================================
@app.callback(
    [Output({"type": "tf-btn", "index": k}, "color") for k in TIMEFRAMES] +
    [Output({"type": "tf-btn", "index": k}, "outline") for k in TIMEFRAMES],
    Input("tf-store", "data"),
)
def update_btn_styles(active_tf):
    colors  = ["primary" if k == active_tf else "secondary" for k in TIMEFRAMES]
    outlines= [False      if k == active_tf else True        for k in TIMEFRAMES]
    return colors + outlines


# ============================================================
#  コールバック: データ取得 → 全UI更新
# ============================================================
@app.callback(
    Output("main-chart",        "figure"),
    Output("signal-card",       "children"),
    Output("signal-card",       "style"),
    Output("stat-price",        "children"),
    Output("stat-rsi",          "children"),
    Output("stat-macd",         "children"),
    Output("stat-score",        "children"),
    Output("indicator-badges",  "children"),
    Output("signal-history",    "children"),
    Output("header-status",     "children"),
    Output("loading-indicator", "children"),
    Input("auto-interval", "n_intervals"),
    Input("refresh-btn",   "n_clicks"),
    Input("tf-store",      "data"),
)
def refresh_all(n_intervals, n_clicks, tf_key):
    tf_key = tf_key or DEFAULT_TF

    # ── データ取得・計算 ──────────────────────────
    try:
        df = fetch_ohlcv(tf_key)
        if df.empty:
            raise ValueError("データなし")
        df = add_indicators(df)
        df = add_signals(df)
        error = None
    except Exception as e:
        error = str(e)

    if error:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0d1117",
            annotations=[dict(text=f"データ取得エラー: {error}",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font=dict(size=14, color="#ef5350"))],
        )
        err_msg = html.Span(f"⚠ {error}", style={"color": "#ef5350"})
        return (empty_fig, err_msg, {}, "", "", "", "", "", "", "", "")

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    now    = datetime.now().strftime("%H:%M:%S")
    score  = float(latest["Score"])
    sig_label, sig_color, sig_bg = signal_label(score)

    # ── チャート ──────────────────────────────────
    fig = build_chart(df, tf_key)

    # ── シグナルカード ────────────────────────────
    price_diff = float(latest["Close"]) - float(prev["Close"])
    price_arrow= "▲" if price_diff >= 0 else "▼"
    price_color= "#26a69a" if price_diff >= 0 else "#ef5350"

    signal_card_children = [
        html.Div(sig_label, style={
            "fontSize": "40px", "fontWeight": "900",
            "color": sig_color, "lineHeight": "1", "letterSpacing": "2px",
        }),
        html.Div(f"スコア: {score:+.1f}", style={
            "fontSize": "13px", "color": sig_color,
            "marginTop": "6px", "opacity": "0.85",
        }),
        html.Div([
            html.Span(f"{price_arrow} ", style={"color": price_color}),
            html.Span(f"{abs(price_diff):.3f}円", style={"color": price_color, "fontSize": "11px"}),
        ], style={"marginTop": "8px", "fontSize": "11px"}),
    ]
    signal_card_style = {
        "borderRadius": "10px",
        "border": f"1px solid {sig_color}",
        "background": sig_bg,
        "padding": "16px",
        "display": "flex", "flexDirection": "column",
        "alignItems": "center", "justifyContent": "center",
        "minHeight": "130px",
        "boxShadow": f"0 0 18px {sig_bg}",
    }

    # ── 統計カード ────────────────────────────────
    def stat(label, value, sub="", val_color="#e6edf3"):
        return [
            html.Div(label, style=CSS["stat_label"]),
            html.Div(value, style={**CSS["stat_value"], "color": val_color}),
            html.Div(sub,   style=CSS["stat_sub"]),
        ]

    close_val = float(latest["Close"])
    rsi_val   = float(latest["RSI"])
    macd_val  = float(latest["MACD"])
    macd_s    = float(latest["MACD_Sig"])

    rsi_color = "#ef5350" if rsi_val > 70 else "#26a69a" if rsi_val < 30 else "#e6edf3"
    macd_color= "#26a69a" if macd_val > macd_s else "#ef5350"

    stat_price = stat("現在値 (JPY)", f"{close_val:.3f}",
                      f"MA{PARAMS['ma_short']}: {float(latest['MA_S']):.3f}")
    stat_rsi   = stat("RSI", f"{rsi_val:.1f}",
                      "過買い >70 / 過売り <30", rsi_color)
    stat_macd  = stat("MACD", f"{macd_val:+.4f}",
                      f"Signal: {macd_s:+.4f}", macd_color)
    stat_score = stat("スコア", f"{score:+.1f}",
                      f"閾値 Buy≥{PARAMS['buy_th']} / Sell≤{PARAMS['sell_th']}", sig_color)

    # ── インジケーター内訳バッジ ──────────────────
    badges_data = [
        (bool(latest["MA_Buy"]),  "✓ MA ゴールデンクロス"),
        (bool(latest["MA_Sell"]), "✗ MA デッドクロス"),
        (bool(latest["MC_Buy"]),  "✓ MACD クロス(買)"),
        (bool(latest["MC_Sell"]), "✗ MACD クロス(売)"),
        (bool(latest["RSI_Buy"]), f"✓ RSI 過売り(<{PARAMS['rsi_oversell']})"),
        (bool(latest["RSI_Sell"]),f"✗ RSI 過買い(>{PARAMS['rsi_overbuy']})"),
        (bool(latest["BB_Buy"]),  "✓ BB 下限タッチ"),
        (bool(latest["BB_Sell"]), "✗ BB 上限タッチ"),
    ]
    badges = [ind_badge(active, label) for active, label in badges_data]

    # ── シグナル履歴 ──────────────────────────────
    history_rows = []
    buy_hist  = df[df["Buy_Signal"]].tail(4)
    sell_hist = df[df["Sell_Signal"]].tail(4)
    all_hist  = pd.concat([
        buy_hist.assign(_type="BUY"),
        sell_hist.assign(_type="SELL"),
    ]).sort_index(ascending=False).head(8)

    for dt, row in all_hist.iterrows():
        stype  = row["_type"]
        color  = "#00e676" if stype == "BUY" else "#ff1744"
        dt_str = str(dt)[:16]
        history_rows.append(
            html.Div(style=CSS["hist_row"], children=[
                html.Span(stype, style={
                    "color": color, "fontWeight": "700",
                    "minWidth": "36px", "fontSize": "12px",
                }),
                html.Span(dt_str, style={"color": "#8b949e", "minWidth": "120px"}),
                html.Span(f"終値: {float(row['Close']):.3f}", style={"minWidth": "100px"}),
                html.Span(f"スコア: {float(row['Score']):+.1f}", style={"color": color}),
            ])
        )

    if not history_rows:
        history_rows = [html.Div("シグナルなし", style={"color": "#8b949e", "fontSize": "12px"})]

    # ── ヘッダーステータス ────────────────────────
    tf_label = TIMEFRAMES[tf_key]["label"]
    header_status = [
        html.Span(f"足種: {tf_label}", style={"marginRight": "14px"}),
        html.Span(f"最終更新: {now}", style={"marginRight": "14px"}),
        html.Span(f"データ数: {len(df)}本"),
    ]

    loading_msg = html.Span(f"✓ {now} 更新完了", style={"color": "#26a69a", "fontSize": "11px"})

    return (
        fig,
        signal_card_children, signal_card_style,
        stat_price, stat_rsi, stat_macd, stat_score,
        badges,
        history_rows,
        header_status,
        loading_msg,
    )


# ============================================================
#  起動
# ============================================================
if __name__ == "__main__":
    print("=" * 52)
    print("  USDJPY FX Analyzer — 起動中")
    print("  ブラウザで http://localhost:8050 にアクセス")
    print("  停止: Ctrl+C")
    print("=" * 52)
    app.run(debug=False, host="0.0.0.0", port=8050)
