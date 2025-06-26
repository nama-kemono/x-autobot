import os
from flask import Flask
from tweepy import Client, TweepyException

app = Flask(__name__)

client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

@app.route("/")
def index():
    return "✅ Bot is running"

@app.route("/test")
def test():
    try:
        resp = client.create_tweet(
            text="APIテスト投稿 " + os.getenv("BEARER_TOKEN", "")[:6],
            user_auth=True  # これが重要（API v2）
        )
        return f"✅ 投稿レスポンス: {resp}"
    except TweepyException as te:
        return f"❌ Tweepyエラー: {te}"
    except Exception as e:
        return f"❌ その他エラー: {e}"

@app.route("/verify")
def verify():
    try:
        me = client.get_me(user_auth=True)
        return f"✅ 認証成功: {me.data.username}"
    except Exception as e:
        return f"❌ 認証失敗: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
