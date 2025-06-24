import os
import schedule
import time
from datetime import datetime
from flask import Flask
import threading
import openai
from tweepy import Client

app = Flask(__name__)

client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

openai.api_key = os.getenv("OPENAI_API_KEY")

def log(msg):
    print(msg)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {msg}\n")

def generate_tweet():
    prompt = "怠け者向け副業やラクして稼ぐことをテーマに、Xに投稿する短いツイートを1つ作ってください。絵文字も使ってください。"
    log("🧠 ChatGPTにリクエスト送信中...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message["content"].strip()
        log("📝 ChatGPT応答: " + content)
        return content
    except Exception as e:
        log("❌ ChatGPT生成エラー: " + str(e))
        return "GPTエラー発生中💥 #副業"

def tweet():
    log("🔔 tweet() 呼び出されました")
    content = generate_tweet()
    try:
        client.create_tweet(text=content)
        log("✅ 投稿成功: " + content)
    except Exception as e:
        log("⚠️ 投稿エラー: " + str(e))

schedule.every().day.at("23:05").do(tweet)
schedule.every().day.at("03:10").do(tweet)
schedule.every().day.at("12:05").do(tweet)

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/test')
def test_post():
    log("📲 /test エンドポイントにアクセスされました")
    tweet()
    return "✅ テスト投稿しました"

@app.route('/logs')
def show_logs():
    try:
        with open("log.txt", "r", encoding="utf-8") as f:
            return "<pre>" + f.read() + "</pre>"
    except Exception as e:
        return f"❌ ログ読み込みエラー: {e}"

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=run_schedule).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
