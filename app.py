import os
import random
import time
import threading
from datetime import datetime, timedelta
from flask import Flask
import openai
from tweepy import Client, TweepyException

app = Flask(__name__)

client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)
openai.api_key = os.getenv("OPENAI_API_KEY")

prompts = {
    "satori": "あなたはTwitter（X）で大人気の「さとり構文」ライターです。以下のような特徴を持つツイートを1つ140字以内で生成してください。...",
    "lazy": "あなたは「ズボラ向け副業アカウント」の中の人です。...",
    "buzz": "あなたはTwitter（X）でバズる投稿を作るプロです。..."
}

keywords = ["副業", "GPT", "お小遣い", "社畜"]

def generate_tweet(style):
    try:
        print(f"[{datetime.now()}] 🔁 Generating tweet with style: {style}")
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompts[style]}],
            temperature=0.9,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error generating tweet:", e)
        return "投稿生成エラー"

def post_tweet():
    style = random.choices(["satori", "lazy", "buzz"], weights=[2, 2, 2])[0]
    tweet = generate_tweet(style)
    print(f"[DEBUG] 生成ツイート内容: {tweet}")
    try:
        response = client.create_tweet(text=tweet)
        print(f"[{datetime.now()}] ✅ Tweet posted: {response}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Failed to post tweet:", e)

def like_and_follow():
    try:
        for keyword in keywords:
            print(f"[{datetime.now()}] 🔍 Searching: {keyword}")
            results = client.search_recent_tweets(query=keyword, max_results=10, tweet_fields=["author_id"])
            print(f"[{datetime.now()}] 🔁 検索件数: {len(results.data) if results.data else 0}")
            if not results.data:
                continue
            for tweet in results.data:
                try:
                    client.like(tweet.id)
                    client.follow_user(tweet.author_id)
                    print(f"✅ いいね・フォロー: {tweet.text[:30]}...")
                    time.sleep(random.randint(60, 120))
                except Exception as inner:
                    print(f"⚠️ アクション失敗: {inner}")
            time.sleep(60 * 15)
    except TweepyException as e:
        print(f"❌ Tweepy エラー: {e}")

def start_posting_loop():
    def loop():
        times = sorted(random.sample(range(7, 22), 10))
        print(f"📅 投稿スケジュール: {[f'{h}:00' for h in times]}")
        for hour in times:
            now = datetime.now()
            next_post = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_post < now:
                next_post += timedelta(days=1)
            wait = (next_post - datetime.now()).total_seconds()
            print(f"⏳ {hour}時まで {int(wait)}秒待機...")
            time.sleep(wait)
            post_tweet()
    threading.Thread(target=loop).start()

def start_like_follow_loop():
    def loop():
        while True:
            like_and_follow()
            print(f"🕒 次のいいね／フォローまで60分待機")
            time.sleep(60 * 60)
    threading.Thread(target=loop).start()

@app.route("/")
def index():
    return "✅ X自動投稿＆いいね・フォローBot稼働中"

@app.route("/test")
def test():
    post_tweet()
    return "✅ テスト投稿完了"

@app.route("/verify")
def verify():
    try:
        me = client.get_me()
        return f"✅ 認証成功: {me.data.username}"
    except Exception as e:
        return f"❌ 認証失敗: {e}"

if __name__ == "__main__":
    start_posting_loop()
    start_like_follow_loop()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
