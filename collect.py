# -*- coding: utf-8 -*-
"""
東京ディズニーランド／シーの待ち時間を Queue-Times の公式APIから記録する。
GitHub Actions 上で15分おきに動かす前提。標準ライブラリだけで動く。

出典表示: Powered by Queue-Times.com
"""
import csv
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request

PARKS = {"274": "land", "275": "sea"}
API = "https://queue-times.com/parks/{park}/queue_times.json"
JST = dt.timezone(dt.timedelta(hours=9))
OPEN_FROM, OPEN_TO = 8 * 60 + 30, 21 * 60 + 15   # 8:30〜21:15（日本時間）
#   ランドのハッピーエントリー（宿泊者の先行入園）は一般ゲストの15分前=8:30 から。
#   8:30〜8:45 は園内がほぼ宿泊者だけになる、この研究で最も価値のある15分。
FIELDS = ["ts_jst", "date_jst", "time_jst", "park_id", "park",
          "ride_id", "ride_name", "is_open", "wait_time", "last_updated"]
HEADERS = {
    "User-Agent": "tdr-research-collector/1.0 (university research; Powered by Queue-Times.com)",
    "Accept": "application/json",
    "Accept-Encoding": "identity",
}


def fetch(park):
    req = urllib.request.Request(API.format(park=park), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def rides_of(obj):
    out = list(obj.get("rides", []))
    for land in obj.get("lands", []):
        out.extend(land.get("rides", []))
    return out


def main():
    now = dt.datetime.now(JST)
    if not (OPEN_FROM <= now.hour * 60 + now.minute < OPEN_TO):
        print("営業時間外 (%s JST) なので記録しません。" % now.strftime("%H:%M"))
        return

    rows = []
    for park, label in PARKS.items():
        try:
            obj = fetch(park)
        except Exception as e:
            print("取得失敗 park=%s: %s" % (park, e))
            time.sleep(2)
            continue
        rides = rides_of(obj)
        for r in rides:
            rows.append({
                "ts_jst": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date_jst": now.strftime("%Y-%m-%d"),
                "time_jst": now.strftime("%H:%M"),
                "park_id": park,
                "park": label,
                "ride_id": r.get("id", ""),
                "ride_name": (r.get("name") or "").replace(",", " ").strip(),
                "is_open": 1 if r.get("is_open") else 0,
                "wait_time": r.get("wait_time", ""),
                "last_updated": r.get("last_updated", ""),
            })
        opened = [x for x in rides if x.get("is_open")]
        waits = [x.get("wait_time", 0) for x in opened]
        print("%s: 乗り物%d件 / 運転中%d件 / 平均%.1f分"
              % (label, len(rides), len(opened),
                 (sum(waits) / len(waits)) if waits else 0))
        time.sleep(1.5)

    if not rows:
        print("書き込む行がありません。")
        return

    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", now.strftime("%Y-%m-%d") + ".csv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    print("%s に %d 行を追記しました。" % (path, len(rows)))


if __name__ == "__main__":
    main()
