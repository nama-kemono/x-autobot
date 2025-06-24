import os
import schedule
import time
from datetime import datetime
from flask import Flask
import threading
from tweepy import Client

app = Flask(__name__)

# 認証（v2エンドポイント用）
client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# 投稿候補（お好きに変更可）
tweets = [
    "Render無料で自動投稿中！ #副業",
    "Flask+schedule構成でBot稼働してます。 #自動化",
    "怠け者のための副業Bot🧠 #ズボラ副業"
]

# 投稿処理
def tweet():
    content = tweets[datetime.now().day % len(tweets)]
    client.create_tweet(text=content)
    print("✅ 投稿:", content)

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
