import os
import schedule
import time
import random
from datetime import datetime
from flask import Flask
import threading
from openai import OpenAI
from tweepy import Client

app = Flask(__name__)

# X (Twitter) API 認証（v2）
client_x = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# OpenAI クライアント初期化
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ログ出力関数
def log(msg):
    print(msg)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {msg}\n")

# 重複ツイート回避のためのバリエーション付加
def append_variation(text):
    suffixes = ["✨", "💡", "✅", "#ズボラ副業", "#らくらく収益"]
    return text + " " + random.choice(suffixes)

# ChatGPTでツイートを生成
def generate_tweet():
    prompt = "怠け者向け副業やラクして稼ぐことをテーマに、Xに投稿する短いツイートを1つ作ってください。絵文字も使ってください。"
    log("🧠 ChatGPTにリクエスト送信中...")
    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o",  # または "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        log("📝 ChatGPT応答: " + content)
        return content
    except Exception as e:
        log("❌ ChatGPT生成エラー: " + str(e))
        return "GPTエラー発生中💥 #副業"

# 投稿処理
def tweet():
    log("🔔 tweet() 呼び出されました")
    content = generate_tweet()
    content = append_variation(content)
    try:
        client_x.create_tweet(text=content)
        log("✅ 投稿成功: " + content)
    except Exception as e:
        log("⚠️ 投稿エラー: " + str(e))

# 日本時間に合わせた投稿スケジュール（UTC）
schedule.every().day.at("23:05").do(tweet)  # 朝8:05
schedule.every().day.at("03:10").do(tweet)  # 昼12:10
schedule.every().day.at("12:05").do(tweet)  # 夜21:05

# Webルート：動作確認
@app.route('/')
def index():
    return "Bot is running!"

# テスト投稿用
@app.route('/test')
def test_post():
    log("📲 /test エンドポイントにアクセスされました")
    tweet()
    return "✅ テスト投稿しました"

# ログ閲覧用
@app.route('/logs')
def show_logs():
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            return "<pre>" + f.read() + "</pre>"
    except Exception as e:
        return f"❌ ログ読み込みエラー: {e}"

# スケジュール実行用スレッド
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# アプリ起動
if __name__ == '__main__':
    threading.Thread(target=run_schedule).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
