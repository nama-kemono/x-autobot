import tweepy
import schedule
import time
from datetime import datetime
from flask import Flask
import os
import threading

app = Flask(__name__)

# APIキー（環境変数から取得）
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

tweets = [
    "Render無料で自動投稿中！",
    "Flask+schedule構成でBot稼働してます。",
    "怠け者のための副業Bot🧠"
]

def tweet():
    content = tweets[datetime.now().day % len(tweets)]
    api.update_status(content)
    print("✅ 投稿:", content)

schedule.every().day.at("09:00").do(tweet)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    threading.Thread(target=run_schedule).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
@app.route('/test')
def test_post():
    tweet()
    return "✅ テスト投稿しました"
