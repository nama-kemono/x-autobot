import os
import random
import time
import threading
from datetime import datetime, timedelta
from flask import Flask
import openai
from tweepy import Client, Paginator, TweepyException

app = Flask(__name__)

# 環境変数の取得
client = Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)
openai.api_key = os.getenv("OPENAI_API_KEY")

# プロンプト定義
prompts = {
    "satori": """あなたはTwitter（X）で大人気の「さとり構文」ライターです。
以下のような特徴を持つツイートを1つ140字以内で生成してください。
【構成の特徴】
1. 冒頭で「○○な人は全員△△を使った方が良い」と断言する。
2. その人が△△を使うことで得られるメリット（効率化・魅力・理解）を具体的に述べる。
3. 一方で反対の性質の人にとっても△△が効果的であると展開する。
4. 結びに「10倍〜になる／見られる／モテる」など、インパクトあるフレーズで締める。
【文体・トーン】
- 一人称や主観を極力排除し、断言口調
- AI、ツール、アプリ、サービス、考え方などを素材にする
- 難しい単語は使わず、ライトでリズムよく
- 箇条書きなし、絵文字なし
対象のテーマは「怠け者と副業とChatGPTの相性」にしてください。""",

    "lazy": """あなたは「ズボラ向け副業アカウント」の中の人です。
パソコンやSNSの知識がない初心者にも伝わる言葉で、毎日自動で投稿が流れる仕組み（完全自動投稿）の魅力を伝えるツイートを、140字以内で1つ生成してください。
【スタイル】
- 会話調、親しみやすい語り口
- 専門用語（Bot、スクリプト、APIなど）は使わない
- 「設定だけで放置」「文章も勝手に考えてくれる」などのキーワードを活用
- あくまでラク・ズボラ・初心者向けという視点を忘れずに
【含めてほしい要素】
- 投稿内容が自動生成されること
- 投稿時間も自動で調整されること
- 最初の1回の設定だけでOKなこと
- それでも毎日投稿されるという驚きとラクさ""",

    "buzz": """あなたはTwitter（X）でバズる投稿を作るプロです。
以下の条件を全て満たす、140字以内の日本語ツイートを1つ作成してください。
【目的】
- 「怠け者 × 副業 × 自動化」をテーマにバズりやすい投稿を生成する。
【構文ルール】
- 冒頭でターゲットのペイン（悩みやイライラ）を具体的に提示
- 解決方法はAI・GPT・自動投稿などで
- ベネフィットは数値・体感・生活の変化として簡潔に示す（例：毎朝10分自由時間が増える！）
- 説明口調を避け、テンポよくユーモアや断言口調を入れる（例：「断言する」「爆速」など）
- カジュアルさを保つ（マジで／一瞬で／ガチで／しんどい etc）
- 冒頭にバズりワード（「こっそり言うけど」「怒られたら消すけど」など）を使ってもOK"""
}

keywords = ["副業", "GPT", "お小遣い", "社畜"]

def generate_tweet(style):
    try:
        print(f"[{datetime.now()}] 🔁 Generating tweet with style: {style}")
        prompt = prompts.get(style)
        print(f"[{datetime.now()}] 💬 Prompt content: {prompt[:100]}...")
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 投稿生成エラー: {e}")
        return "投稿生成エラー"

def post_tweet():
    style = random.choices(["satori", "lazy", "buzz"], weights=[2, 2, 2])[0]
    tweet = generate_tweet(style)
    try:
        client.create_tweet(text=tweet)
        print(f"[{datetime.now()}] ✅ Tweet posted: {tweet}")
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
    return "✅ X自動投稿＆いいね・フォローボット稼働中"

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
