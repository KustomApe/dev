#!/usr/bin/env python3
"""
FX経済指標アラームBot
======================
Forex Factory の公開APIから今週の経済指標を取得し、
指定時間前にデスクトップ通知 / Slack通知を送るBotです。

依存ライブラリのインストール:
    pip install requests schedule plyer

オプション(Slack通知):
    pip install slack_sdk

使い方:
    python fx_economic_calendar_bot.py

設定:
    スクリプト上部の CONFIG セクションを編集してください。
"""

import json
import time
import threading
import datetime
import requests
import schedule

# ─────────────────────────────────────────────
# CONFIG (ここを編集してください)
# ─────────────────────────────────────────────

CONFIG = {
    # 通知対象の通貨 (空リストで全通貨)
    "currencies": ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD"],

    # 通知対象のインパクト: "High" / "Medium" / "Low"
    "min_impact": "High",

    # 何分前に通知するか
    "alert_minutes_before": [60, 15, 5],

    # デスクトップ通知を使うか
    "desktop_notify": True,

    # Slack通知 (使わない場合は None)
    "slack_webhook_url": None,
    # 例: "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"

    # タイムゾーン補正 (UTC+9 = 9)
    "timezone_offset_hours": 9,
}

# ─────────────────────────────────────────────
# 経済指標カレンダーの取得
# ─────────────────────────────────────────────

CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

IMPACT_RANK = {"High": 3, "Medium": 2, "Low": 1, "Holiday": 0}


def fetch_calendar() -> list[dict]:
    """Forex Factory から今週のカレンダーを取得する。"""
    try:
        resp = requests.get(CALENDAR_URL, timeout=10)
        resp.raise_for_status()
        events = resp.json()
        print(f"[取得完了] {len(events)} 件のイベントを取得しました")
        return events
    except Exception as e:
        print(f"[エラー] カレンダー取得失敗: {e}")
        return []


def filter_events(events: list[dict]) -> list[dict]:
    """設定に基づいてイベントをフィルタリングする。"""
    min_rank = IMPACT_RANK.get(CONFIG["min_impact"], 3)
    currencies = set(CONFIG["currencies"])
    result = []

    for ev in events:
        impact = ev.get("impact", "Low")
        currency = ev.get("currency", "")
        if IMPACT_RANK.get(impact, 0) >= min_rank:
            if not currencies or currency in currencies:
                result.append(ev)

    return result


def parse_event_time(ev: dict) -> datetime.datetime | None:
    """イベントのUTC時刻をパースしてローカル時刻に変換する。"""
    raw = ev.get("date", "")
    if not raw:
        return None
    try:
        # Forex Factoryは "2024-01-15T13:30:00-05:00" 形式
        dt = datetime.datetime.fromisoformat(raw)
        # UTC に正規化
        if dt.tzinfo:
            import datetime as dt_mod
            utc_offset = dt.utcoffset()
            dt_utc = dt.replace(tzinfo=None) - utc_offset
        else:
            dt_utc = dt
        # ローカル時刻に変換
        local = dt_utc + datetime.timedelta(hours=CONFIG["timezone_offset_hours"])
        return local
    except Exception:
        return None


# ─────────────────────────────────────────────
# 通知
# ─────────────────────────────────────────────

def notify_desktop(title: str, message: str):
    """デスクトップ通知を送信する (plyer)。"""
    if not CONFIG["desktop_notify"]:
        return
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="FX Economic Bot",
            timeout=10,
        )
    except ImportError:
        print("[INFO] plyer がインストールされていません。pip install plyer で追加できます。")
    except Exception as e:
        print(f"[通知エラー] {e}")


def notify_slack(title: str, message: str):
    """Slack Webhook に通知を送信する。"""
    url = CONFIG.get("slack_webhook_url")
    if not url:
        return
    try:
        payload = {"text": f"*{title}*\n{message}"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[Slackエラー] {e}")


def fire_alert(ev: dict, minutes_before: int, local_time: datetime.datetime):
    """アラートを発火する。"""
    impact_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(ev.get("impact", ""), "⚪")
    currency = ev.get("currency", "?")
    title_str = ev.get("title", "不明なイベント")
    forecast = ev.get("forecast", "-")
    previous = ev.get("previous", "-")
    time_str = local_time.strftime("%H:%M")

    if minutes_before == 0:
        header = f"⚡ {impact_icon} 今すぐ: {currency} {title_str}"
    else:
        header = f"⏰ {impact_icon} {minutes_before}分後: {currency} {title_str}"

    body = (
        f"時刻: {time_str}\n"
        f"予想: {forecast}  前回: {previous}"
    )

    print(f"\n{'='*50}")
    print(header)
    print(body)
    print(f"{'='*50}")

    notify_desktop(header, body)
    notify_slack(header, body)


# ─────────────────────────────────────────────
# スケジューラ
# ─────────────────────────────────────────────

_scheduled_alerts: set[str] = set()


def schedule_alerts(events: list[dict]):
    """フィルタ済みイベントに対してアラートをスケジュールする。"""
    now = datetime.datetime.now()
    count = 0

    for ev in events:
        local_time = parse_event_time(ev)
        if local_time is None:
            continue

        for minutes_before in CONFIG["alert_minutes_before"]:
            alert_at = local_time - datetime.timedelta(minutes=minutes_before)
            if alert_at <= now:
                continue  # 過去のアラートはスキップ

            # 重複防止キー
            key = f"{ev.get('title','')}_{local_time.isoformat()}_{minutes_before}"
            if key in _scheduled_alerts:
                continue
            _scheduled_alerts.add(key)

            # クロージャでキャプチャ
            def make_job(e=ev, m=minutes_before, t=local_time):
                def job():
                    fire_alert(e, m, t)
                    return schedule.CancelJob
                return job

            delay_sec = (alert_at - now).total_seconds()
            # バックグラウンドスレッドでタイマー起動
            timer = threading.Timer(delay_sec, make_job())
            timer.daemon = True
            timer.start()
            count += 1
            print(
                f"[スケジュール] {ev.get('currency')} {ev.get('title')} "
                f"→ {minutes_before}分前 ({alert_at.strftime('%m/%d %H:%M')})"
            )

    print(f"\n✅ {count} 件のアラートをスケジュールしました")


# ─────────────────────────────────────────────
# 今週のイベント一覧表示
# ─────────────────────────────────────────────

def print_weekly_schedule(events: list[dict]):
    """今週の重要イベントをコンソールに表示する。"""
    print("\n" + "=" * 60)
    print("📅 今週の重要経済指標")
    print("=" * 60)

    current_date = None
    for ev in events:
        local_time = parse_event_time(ev)
        if local_time is None:
            continue

        date_str = local_time.strftime("%m/%d (%a)")
        if date_str != current_date:
            current_date = date_str
            print(f"\n── {date_str} ──")

        impact = ev.get("impact", "Low")
        icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(impact, "⚪")
        print(
            f"  {icon} {local_time.strftime('%H:%M')}  "
            f"{ev.get('currency', '  '):4s}  "
            f"{ev.get('title', ''):<40s}  "
            f"予想:{ev.get('forecast','-'):>8s}  前回:{ev.get('previous','-'):>8s}"
        )

    print("\n" + "=" * 60)


# ─────────────────────────────────────────────
# カレンダーの週次更新
# ─────────────────────────────────────────────

def refresh_calendar():
    """カレンダーを再取得してスケジュールを更新する。"""
    print("\n[更新] カレンダーを再取得中...")
    events = fetch_calendar()
    filtered = filter_events(events)
    print_weekly_schedule(filtered)
    schedule_alerts(filtered)


# ─────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🤖 FX経済指標アラームBot 起動")
    print(f"   対象通貨: {', '.join(CONFIG['currencies']) or '全通貨'}")
    print(f"   最低インパクト: {CONFIG['min_impact']}")
    print(f"   通知タイミング: {CONFIG['alert_minutes_before']} 分前")
    print(f"   タイムゾーン: UTC+{CONFIG['timezone_offset_hours']}")
    print("=" * 60)

    # 起動時に即時取得
    refresh_calendar()

    # 毎週月曜0時に再取得
    schedule.every().monday.at("00:01").do(refresh_calendar)
    # 毎日0時にも再取得（日付境界対応）
    schedule.every().day.at("00:01").do(refresh_calendar)

    print("\n⏳ 監視中... (Ctrl+C で終了)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n👋 Botを終了しました")


if __name__ == "__main__":
    main()
