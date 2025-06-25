import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)

api = tweepy.API(auth)

try:
    user = api.verify_credentials()
    if user:
        print(f"✅ 認証成功: {user.screen_name}")
    else:
        print("❌ 認証失敗（ユーザー情報なし）")
except Exception as e:
    print("❌ エラー:", e)
