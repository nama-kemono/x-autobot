import tweepy
import os
import random

def generate_post():
    prompts = [
        "さとり構文スタイルのツイート文例。",
        "ズボラ向け完全自動投稿スタイルのツイート文例。",
        "バズ構文スタイルのツイート文例。"
    ]
    return random.choice(prompts)

def post_tweet():
    tweet_text = generate_post()
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
        )
        client.create_tweet(text=tweet_text)
        print("✅ ツイート送信成功！")
        return True
    except Exception as e:
        print("❌ ツイート送信エラー:", e)
        return False