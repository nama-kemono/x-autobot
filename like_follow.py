
import random

def auto_like_and_follow(client):
    keywords = ["副業", "GPT", "お小遣い", "社畜"]
    keyword = random.choice(keywords)
    response = client.search_recent_tweets(query=keyword, max_results=10)

    for tweet in response.data:
        try:
            client.like(tweet.id, user_auth=True)
            client.follow(tweet.author_id, user_auth=True)
            print(f"✅ いいね＆フォロー: {tweet.id}")
        except Exception as e:
            print(f"❌ 処理エラー: {e}")
