
import os
from flask import Flask
import tweepy

app = Flask(__name__)

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

@app.route("/verify")
def verify():
    try:
        user = client.get_me()
        return f"✅ 認証成功: {user.data.username}"
    except Exception as e:
        return f"❌ 認証失敗: {e}"

@app.route("/test")
def test_post():
    try:
        client.create_tweet(text="テスト投稿 from tweepy.Client")
        return "✅ 投稿成功"
    except Exception as e:
        return f"❌ ツイート失敗: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
