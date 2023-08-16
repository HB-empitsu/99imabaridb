# flaskモジュールからFlaskクラスをインポート
from flask import Flask, render_template, redirect

import datetime

# スケジュール実行
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# sqlite3をインポート
import sqlite3

# データベース
DATABASE_FILE = "imabariHosp.db"

# カラム名
col_name = [
    "id",
    "date",
    "week",
    "name",
    "address",
    "tel",
    "night_tel",
    "type",
    "day_time",
    "night_time",
    "date_week",
    "time",
    "lat",
    "lon",
    "navi",
]

# Flaskクラスをインスタンス化してapp変数に代入
app = Flask(__name__)


# 今日を表示
@app.route("/")
def today_get():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日までのデータを抽出する
    c.execute(
        "SELECT DISTINCT date, week, date_week FROM hospital WHERE date <= date('now', 'localtime') ORDER BY date ASC"
    )

    dates = c.fetchall()

    posts_by_hosp = {}

    for date in dates:
        c.execute("SELECT * FROM hospital WHERE date=?", (date[0],))
        posts_by_hosp[date[2]] = [dict(zip(col_name, i)) for i in c.fetchall()]

    # データベースの接続を終了
    c.close()

    return render_template("index.html", posts_by_hosp=posts_by_hosp)


# 今月を表示
@app.route("/list")
def month_get():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 全データを抽出する
    c.execute("SELECT DISTINCT date, week, date_week FROM hospital ORDER BY date ASC")

    dates = c.fetchall()

    posts_by_hosp = {}

    for date in dates:
        c.execute("SELECT * FROM hospital WHERE date=?", (date[0],))
        posts_by_hosp[date[2]] = [dict(zip(col_name, i)) for i in c.fetchall()]

    # データベースの接続を終了
    c.close()

    return render_template("list.html", posts_by_hosp=posts_by_hosp)


# お知らせを表示
@app.route("/info")
def link_get():
    # 広報いまばりのURL生成のために年月を作成
    dt_now = datetime.datetime.now()
    return render_template("info.html", post_date=f"{dt_now:%Y%m}")


# 404エラーは今日へ移動
@app.errorhandler(404)
def page_not_found(error):
    return redirect("/")


# スケジュール削除


# 前日を削除
def delete_yesterday():
    # データベース準備
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 前日のデータを削除
    c.execute("DELETE FROM hospital WHERE date < date('now', 'localtime')")

    # データベースを更新
    conn.commit()

    # データベースの接続を終了
    c.close()


# 今日の指定なし以外（内科・小児科・島しょ部）を削除
def delete_daytime():
    # データベース準備
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日の指定なし以外を削除
    c.execute(
        "DELETE FROM hospital WHERE date = date('now', 'localtime') AND type <> '指定なし'"
    )

    # データベースを更新
    conn.commit()

    # データベースの接続を終了
    c.close()


# 初回起動時に上記データベース削除を実行する
delete_yesterday()
delete_daytime()

# スクリプトとして直接実行した場合
if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    # 毎日09:00にdelete_yesterday関数を実行するジョブを追加
    trigger_09 = CronTrigger(hour=9, minute=0)
    scheduler.add_job(delete_yesterday, trigger=trigger_09)

    # 毎日18:00にdelete_daytime関数を実行するジョブを追加
    trigger_18 = CronTrigger(hour=18, minute=0)
    scheduler.add_job(delete_daytime, trigger=trigger_18)

    scheduler.start()

    # FlaskのWEBアプリケーションを起動
    # app.run(debug=True)

    # 外部アクセス可
    app.run(debug=True, host="0.0.0.0", port=5050)
