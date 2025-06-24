
import os
import schedule
import time
from datetime import datetime
from flask import Flask
import threading
from openai import OpenAI
from tweepy import Client

app = Flask(__name__)

# X API 認証（v2）
client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# OpenAI API 認証
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ChatGPTで投稿を生成
def generate_tweet():
    prompt = "怠け者向け副業やラクして稼ぐことをテーマに、Xに投稿する短いツイートを1つ作ってください。絵文字も使ってください。"
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    content = response.choices[0].message.content.strip()
    return content

# 投稿実行
def tweet():
    try:
        content = generate_tweet()
        client.create_tweet(text=content)
        print("✅ 投稿:", content)
    except Exception as e:
        print("⚠️ 投稿エラー:", e)

# 日本時間に合わせた3回投稿（UTC）
schedule.every().day.at("23:05").do(tweet)  # 朝8:05
schedule.every().day.at("03:10").do(tweet)  # 昼12:10
schedule.every().day.at("12:05").do(tweet)  # 夜21:05

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/test')
def test_post():
    tweet()
    return "✅ テスト投稿しました"

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=run_schedule).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
