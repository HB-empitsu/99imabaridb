# flaskモジュールからFlaskクラスをインポート
from flask import Flask, render_template, redirect

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


@app.route("/")
def today_get():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日のデータを抽出する
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


@app.route("/list")
def month_get():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日のデータを抽出する
    c.execute("SELECT DISTINCT date, week, date_week FROM hospital ORDER BY date ASC")

    dates = c.fetchall()

    posts_by_hosp = {}

    for date in dates:
        c.execute("SELECT * FROM hospital WHERE date=?", (date[0],))
        posts_by_hosp[date[2]] = [dict(zip(col_name, i)) for i in c.fetchall()]

    # データベースの接続を終了
    c.close()

    return render_template("list.html", posts_by_hosp=posts_by_hosp)


@app.route("/info")
def link_get():
    return render_template("info.html")


@app.errorhandler(404)
def page_not_found(error):
    return redirect("/")


# スケジュール削除


def delete_yesterday():
    # データベース準備
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日のデータを抽出する
    c.execute("DELETE FROM hospital WHERE date < date('now', 'localtime')")

    # データベースを更新
    conn.commit()

    # データベースの接続を終了
    c.close()


def delete_daytime():
    # データベース準備
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # 今日のデータを抽出する
    c.execute(
        "DELETE FROM hospital WHERE date = date('now', 'localtime') AND type <> '指定なし'"
    )

    # データベースを更新
    conn.commit()

    # データベースの接続を終了
    c.close()


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
    app.run(debug=True)
