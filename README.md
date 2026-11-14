# tdr-waits

東京ディズニーランド／東京ディズニーシーのアトラクション待ち時間を15分おきに記録しています。大学の授業の課題として作成したものです。

## Powered by Queue-Times.com

https://queue-times.com/

待ち時間データは Queue-Times.com の公開APIから取得しています。同サイトは、パークが公式に公表している待ち時間を自動収集したものと説明しています。

## 中身

- collect.py … 取得スクリプト。標準ライブラリのみで動きます
- .github/workflows/collect.yml … 1日3コマに分けて自動実行します
- data/YYYY-MM-DD.csv … 1日1ファイル。日本時間 8:30〜22:00 を15分おき

## 列

ts_jst, date_jst, time_jst, park_id, park, ride_id, ride_name, is_open, wait_time, last_updated

park_id は 274 が東京ディズニーランド、275 が東京ディズニーシーです。
