import tweepy
import schedule
import time
from datetime import datetime
import os

# Render環境変数から取得
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# 認証
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# 投稿内容（ローテーション式）
tweets = [
    "Renderから自動投稿！#ズボラ副業",
    "自動投稿Bot、今も動いてます。",
    "放置型SNS運用で副業をラクに。"
]

def tweet():
    content = tweets[datetime.now().day % len(tweets)]
    api.update_status(content)
    print("✅ 投稿完了:", content)

# 毎日9:00に投稿（テストなら時間変更もOK）
schedule.every().day.at("09:00").do(tweet)

# 常時監視ループ（Render上で動き続ける）
while True:
    schedule.run_pending()
    time.sleep(1)
