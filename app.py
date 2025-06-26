
import os
import random
import time
from datetime import datetime
from flask import Flask
from dotenv import load_dotenv
from tweepy import Client, TweepyException
from prompts import generate_prompt
from like_follow import auto_like_and_follow

load_dotenv()
app = Flask(__name__)

client = Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
    bearer_token=os.getenv("BEARER_TOKEN"),
    wait_on_rate_limit=True
)

def post_tweet():
    try:
        tweet = generate_prompt()
        response = client.create_tweet(text=tweet, user_auth=True)
        print(f"✅ ツイート成功: {response.data}")
    except TweepyException as e:
        print(f"❌ ツイート失敗: {e}")

@app.route("/")
def index():
    return "✅ Twitter Bot is running."

@app.route("/test")
def test():
    try:
        tweet = generate_prompt()
        response = client.create_tweet(text=tweet, user_auth=True)
        return f"✅ テスト投稿完了: {response.data}"
    except TweepyException as e:
        return f"❌ 投稿失敗: {e}"

@app.route("/like_follow")
def like_follow():
    try:
        auto_like_and_follow(client)
        return "✅ いいね＆フォロー完了"
    except Exception as e:
        return f"❌ エラー: {e}"

if __name__ == "__main__":
    print("📅 投稿スケジュール: ['8:00', '12:00', '18:00']")
    app.run(host="0.0.0.0", port=10000)
