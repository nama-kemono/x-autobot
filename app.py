import os
import random
import time
import threading
from datetime import datetime, timedelta
from flask import Flask
import openai
from tweepy import Client, TweepyException

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
    print(f"[GEN_TWEET] style={style}", flush=True)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompts[style]}],
            temperature=0.9,
        )
        print("[GEN_TWEET] openai応答:", response, flush=True)
        content = response.choices[0].message["content"].strip()
        print(f"[GEN_TWEET] content={content}", flush=True)
        return content
    except Exception as e:
        print("[GEN_TWEET] AI生成エラー:", e, flush=True)
        return "投稿生成エラー"

def post_tweet():
    print("[POST_TWEET] 呼び出しOK", flush=True)
    style = random.choices(["satori", "lazy", "buzz"], weights=[2, 2, 2])[0]
    print(f"[POST_TWEET] 選択style={style}", flush=True)
    tweet = generate_tweet(style)
    print(f"[POST_TWEET] 生成文: {tweet}", flush=True)
    try:
        response = client.create_tweet(text=tweet)
        print(f"[POST_TWEET] 投稿レスポンス: {response}", flush=True)
    except Exception as e:
        print(f"[POST_TWEET] 投稿失敗: {e}", flush=True)

def like_and_follow():
    try:
        for keyword in keywords:
            print(f"[LIKE_FOLLOW] 🔍 Searching: {keyword}", flush=True)
            results = client.search_recent_tweets(query=keyword, max_results=10, tweet_fields=["author_id"])
            print(f"[LIKE_FOLLOW] 🔁 検索件数: {len(results.data) if results.data else 0}", flush=True)
            if not results.data:
                continue
            for tweet in results.data:
                try:
                    client.like(tweet.id)
                    client.follow_user(tweet.author_id)
                    print(f"[LIKE_FOLLOW] ✅ いいね・フォロー: {tweet.text[:30]}...", flush=True)
                    time.sleep(random.randint(60, 120))  # 各アクションの間隔
                except Exception as inner:
                    print(f"[LIKE_FOLLOW] ⚠️ アクション失敗: {inner}", flush=True)
            time.sleep(60 * 15)  # キーワードごとに15分空ける
    except TweepyException as e:
        print(f"[LIKE_FOLLOW] ❌ Tweepy エラー: {e}", flush=True)

def start_posting_loop():
    def loop():
        times = sorted(random.sample(range(7, 22), 10))
        print(f"[POST_LOOP] 📅 投稿スケジュール: {[f'{h}:00' for h in times]}", flush=True)
        for hour in times:
            now = datetime.now()
            next_post = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_post < now:
                next_post += timedelta(days=1)
            wait = (next_post - datetime.now()).total_seconds()
            print(f"[POST_LOOP] ⏳ {hour}時まで {int(wait)}秒待機...", flush=True)
            time.sleep(wait)
            post_tweet()
    threading.Thread(target=loop, daemon=True).start()

def start_like_follow_loop():
    def loop():
        while True:
            like_and_follow()
            print(f"[LIKE_FOLLOW_LOOP] 🕒 次のいいね／フォローまで60分待機", flush=True)
            time.sleep(60 * 60)
    threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def index():
    print("[ROUTE] / index accessed", flush=True)
    return "✅ X自動投稿＆いいね・フォローBot稼働中"

@app.route("/test")
def test():
    print("[ROUTE] /testエンドポイント呼ばれた！", flush=True)
    try:
        post_tweet()
        print("[ROUTE] post_tweet()呼び出し完了", flush=True)
    except Exception as e:
        print("[ROUTE] post_tweet()例外:", e, flush=True)
    return "✅ テスト投稿完了"

@app.route("/verify")
def verify():
    try:
        me = client.get_me()
        print(f"[VERIFY] 認証成功: {me.data.username}", flush=True)
        return f"✅ 認証成功: {me.data.username}"
    except Exception as e:
        print(f"[VERIFY] 認証失敗: {e}", flush=True)
        return f"❌ 認証失敗: {e}"

if __name__ == "__main__":
    print("[MAIN] サービス起動", flush=True)
    start_posting_loop()
    start_like_follow_loop()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
