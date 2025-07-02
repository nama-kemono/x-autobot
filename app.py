import os
import random
import threading
import time
import datetime
from flask import Flask
import tweepy
import openai

# --- 環境変数取得 ---
CONSUMER_KEY        = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET     = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN        = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
BEARER_TOKEN        = os.environ["BEARER_TOKEN"]
OPENAI_API_KEY      = os.environ["OPENAI_API_KEY"]

# --- Tweepy Client（API v2） ---
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# --- OpenAI API keyセット ---
openai.api_key = OPENAI_API_KEY

# --- 投稿用プロンプト設定 ---
prompts = {
    "satori": """あなたはSNSで“売れる投稿”を作るプロのコピーライターです。  
以下の条件に基づいて、自然な長文ポスト（200〜280文字）生成してください。   
各ポストはX（旧Twitter）用の内容で、1ツイートに収まらなくても構いません。  
構成・文体・目的に従って、人間の感情を動かし、自然に行動へ導く流れで作成してください。

【ターゲット】：X投稿が継続できない怠け者の会社員  
【ジャンル・テーマ】：SNSマーケティング、副業、集客  
【販売商品】：初期設定だけでXの完全自動投稿（ChatGpt＋予約投稿）ができるマニュアル  
【目的】：システムを導入すれば「継続できる／投稿に悩まない／放置でも売れる」未来があることを伝える  

【構成テンプレ】：  
① 共感（読者の痛みや悩み）  
② 本質の説明（なぜそれが起こるのか）  
③ 解決策の提案（ChatGPT＋自動投稿システム）  
④ 未来のイメージ（ベネフィット）  
⑤ 行動の促し（自然なCTA）  
※毎回、下記の固定CTA文をポスト末尾に必ず追加してください。

【文体ルール】：  
・本文中には絵文字・ハッシュタグを使わない（※CTA部は例外）  
・自然な日本語。読点と改行を適度に使い、読みやすい構成にする  
・口調はカジュアル～誠実の中間  
・1投稿あたり200〜280文字  

【固定CTA】  
【特典配布中🎁】
""",

    
}

# --- 投稿スケジュール設定 ---
POST_TIMES = ['8:00', '12:00', '19:00', '21:00']
RANDOMIZE_MINUTES = 7  # ±7分ズラす

def get_next_post_time(now=None):
    if now is None:
        now = datetime.datetime.now()
    today = now.date()
    possible_times = []
    for t in POST_TIMES:
        hour, minute = map(int, t.split(':'))
        base_time = datetime.datetime.combine(today, datetime.time(hour, minute))
        delta = random.randint(-RANDOMIZE_MINUTES, RANDOMIZE_MINUTES)
        post_time = base_time + datetime.timedelta(minutes=delta)
        if post_time > now:
            possible_times.append(post_time)
    if not possible_times:
        t = POST_TIMES[0]
        hour, minute = map(int, t.split(':'))
        base_time = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(hour, minute))
        delta = random.randint(-RANDOMIZE_MINUTES, RANDOMIZE_MINUTES)
        post_time = base_time + datetime.timedelta(minutes=delta)
        return post_time
    return min(possible_times)

def generate_tweet(style):
    prompt = prompts[style]
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=140,
            temperature=0.95,
            n=1,
            stop=None,
        )
        tweet = response.choices[0].message.content.strip().replace('\n', '')
        if len(tweet) > 140:
            tweet = tweet[:137] + "…"
        return tweet
    except Exception as e:
        print(f"[GEN_TWEET] AI生成エラー: {e}", flush=True)
        return "投稿生成エラー"

def post_tweet(style):
    tweet = generate_tweet(style)
    print(f"[POST_TWEET] 生成文: {tweet}", flush=True)
    max_retry = 2  # 最大2回リトライ
    for attempt in range(max_retry + 1):
        try:
            resp = client.create_tweet(text=tweet)
            print(f"[POST_TWEET] 投稿レスポンス: {resp}", flush=True)
            return True
        except Exception as e:
            print(f"[POST_TWEET] 投稿失敗（{attempt+1}回目）: {e}", flush=True)
            if "429" in str(e):
                print("[POST_TWEET] 429エラー検知→リトライせず終了", flush=True)
                break
            if attempt < max_retry:
                time.sleep(2)
    return False

def post_loop():
    while True:
        now = datetime.datetime.now()
        next_time = get_next_post_time(now)
        sec = (next_time - now).total_seconds()
        print(f"[POST_LOOP] ⏳ {next_time.strftime('%H:%M')}まで {int(sec)}秒待機...", flush=True)
        time.sleep(max(0, sec))
        style = random.choice(list(prompts.keys()))
        print(f"[POST_LOOP] 投稿style={style}", flush=True)
        post_tweet(style)

# --- いいね＆フォロー（制限対応） ---
LIKE_FOLLOW_KEYWORDS = ["副業", "在宅ワーク", "ズボラ", "自動投稿", "ChatGPT", "お小遣い"]
LIKE_FOLLOW_INTERVAL = 60 * 60 * 12  # 12時間（秒）

def like_and_follow():
    count = 0
    for keyword in random.sample(LIKE_FOLLOW_KEYWORDS, min(10, len(LIKE_FOLLOW_KEYWORDS))):
        if count >= 10:
            break
        try:
            results = client.search_recent_tweets(query=keyword, max_results=10, tweet_fields=["author_id"])
            if results.data:
                for tweet in results.data:
                    try:
                        client.like(tweet.id)
                        client.follow_user(tweet.author_id)
                        print(f"いいね・フォロー: {tweet.text[:30]}...", flush=True)
                        count += 1
                        time.sleep(3600)
                        if count >= 10:
                            break
                    except Exception as inner:
                        print(f"アクション失敗: {inner}", flush=True)
                        if "429" in str(inner):
                            print("429エラー！12時間休憩", flush=True)
                            time.sleep(60 * 60 * 12)
                            return
        except Exception as e:
            print(f"[LIKE_FOLLOW] ❌ Tweepy エラー: {e}", flush=True)

# --- Flaskルート ---
app = Flask(__name__)

@app.route("/")
def index():
    return "X AutoBot 起動中"

@app.route("/test", methods=["GET"])
def test_post():
    print("[ROUTE] /testエンドポイント呼ばれた！", flush=True)
    try:
        text = generate_tweet("satori")
        print("[POST_TWEET] 呼び出しOK", flush=True)
        print("[POST_TWEET] 生成文:", text, flush=True)
        max_retry = 2
        for attempt in range(max_retry + 1):
            try:
                resp = client.create_tweet(text=text)
                print("[POST_TWEET] 投稿レスポンス:", resp, flush=True)
                return "OK"
            except Exception as e:
                print(f"[POST_TWEET] 投稿失敗（{attempt+1}回目）: {e}", flush=True)
                if "429" in str(e):
                    print("[POST_TWEET] 429エラー検知→リトライせず終了", flush=True)
                    break
                if attempt < max_retry:
                    time.sleep(2)
        return "NG", 500
    except Exception as e:
        print("[POST_TWEET] 投稿生成処理失敗:", e, flush=True)
        return "NG", 500

# --- メインスレッド起動 ---
def like_follow_loop():
    while True:
        like_and_follow()
        time.sleep(LIKE_FOLLOW_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=post_loop, daemon=True).start()
    threading.Thread(target=like_follow_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
