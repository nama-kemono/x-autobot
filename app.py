import os
import random
import threading
import time
import datetime
from flask import Flask
import tweepy
import openai

# --- 環境変数取得（key名は全て大文字） ---
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

# --- 投稿スケジュール（例：毎時00分に投稿。ランダム幅で±7分ズラす） ---
POST_TIMES = ['7:00', '8:00', '12:00', '13:00', '14:00', '15:00', '17:00', '19:00', '20:00', '21:00']
RANDOMIZE_MINUTES = 7  # プラスマイナス最大7分

def get_next_post_time(now=None):
    """次回投稿予定の時刻（ランダムずらし適用）を返す"""
    if now is None:
        now = datetime.datetime.now()
    today = now.date()
    possible_times = []
    for t in POST_TIMES:
        hour, minute = map(int, t.split(':'))
        base_time = datetime.datetime.combine(today, datetime.time(hour, minute))
        # ランダム幅（-7〜+7分）でずらし
        delta = random.randint(-RANDOMIZE_MINUTES, RANDOMIZE_MINUTES)
        post_time = base_time + datetime.timedelta(minutes=delta)
        if post_time > now:
            possible_times.append(post_time)
    if not possible_times:
        # 翌日1件目にする
        t = POST_TIMES[0]
        hour, minute = map(int, t.split(':'))
        base_time = datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.time(hour, minute))
        delta = random.randint(-RANDOMIZE_MINUTES, RANDOMIZE_MINUTES)
        post_time = base_time + datetime.timedelta(minutes=delta)
        return post_time
    return min(possible_times)

def generate_tweet(style):
    """OpenAIでツイートを生成"""
    prompt = prompts[style]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは日本語のTwitter(X)投稿作成AIです。140字以内で返答してください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.95,
            n=1,
            stop=None,
        )
        tweet = response.choices[0].message.content.strip().replace('\n', '')
        if len(tweet) > 140:
            tweet = tweet[:137] + "…"
        return tweet
    except Exception as e:
        print(f"[GEN_TWEET] AI生成エラー: {e}")
        return "投稿生成エラー"

def post_tweet(style):
    """ツイート生成＋投稿"""
    tweet = generate_tweet(style)
    print(f"[POST_TWEET] 生成文: {tweet}")
    try:
        response = client.create_tweet(text=tweet)
        print(f"[POST_TWEET] 投稿レスポンス: {response}")
    except Exception as e:
        print(f"[POST_TWEET] 投稿失敗: {e}")

def post_loop():
    """スケジューリング投稿のループ"""
    while True:
        now = datetime.datetime.now()
        next_time = get_next_post_time(now)
        sec = (next_time - now).total_seconds()
        print(f"[POST_LOOP] ⏳ {next_time.strftime('%H:%M')}まで {int(sec)}秒待機...")
        time.sleep(max(0, sec))
        style = random.choice(list(prompts.keys()))
        print(f"[POST_LOOP] 投稿style={style}")
        post_tweet(style)

# --- Flaskルート ---
app = Flask(__name__)

@app.route("/")
def index():
    return "X AutoBot 起動中"

@app.route("/test", methods=["GET"])
def test_post():
    print("[ROUTE] /testエンドポイント呼ばれた！")
    try:
        text = generate_tweet("lazy")  # 例: "lazy" スタイル
        print("[POST_TWEET] 呼び出しOK")
        print("[POST_TWEET] 生成文:", text)
        resp = client.create_tweet(text=text)
        print("[POST_TWEET] 投稿レスポンス:", resp)
        return "OK"
    except Exception as e:
        print("[POST_TWEET] 投稿失敗:", e)
        return "NG", 500
