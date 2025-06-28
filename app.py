import os
import time
import random
import traceback
from datetime import datetime, timedelta
from threading import Thread

from flask import Flask, jsonify
import tweepy
from openai import OpenAI
from dotenv import load_dotenv

# ----------------------------
# 環境変数ロード
# ----------------------------
load_dotenv()

client = tweepy.Client(
    consumer_key=os.environ["X_CONSUMER_KEY"],
    consumer_secret=os.environ["X_CONSUMER_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
)

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 投稿スケジュール（分は必ず00でOK）
POST_SCHEDULES = [
    "8:00", "9:00", "10:00", "11:00", "12:00", "14:00", "16:00", "18:00", "19:00", "20:00"
]
POST_TIME_RANDOM_RANGE = 7  # 投稿時刻±7分

# --- 最新プロンプト群 ---
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

# Flaskサーバ
app = Flask(__name__)

# ----------------------------
# 投稿生成ロジック
# ----------------------------
def generate_tweet(style="satori"):
    prompt = prompts.get(style, prompts["lazy"])
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはSNS自動化のプロです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
        )
        content = resp.choices[0].message.content.strip()
        return content
    except Exception as e:
        print("[GEN_TWEET] AI生成エラー:", e)
        traceback.print_exc()
        return "投稿生成エラー"

# ----------------------------
# 投稿実行
# ----------------------------
def post_tweet(style=None):
    if style is None:
        style = random.choice(list(prompts.keys()))
    print(f"[POST_TWEET] 選択style={style}")
    text = generate_tweet(style=style)
    print(f"[POST_TWEET] 生成文: {text}")
    try:
        response = client.create_tweet(text=text)
        print(f"[POST_TWEET] 投稿レスポンス: {response}")
    except Exception as e:
        print("[POST_TWEET] 投稿失敗:", e)
        traceback.print_exc()

# ----------------------------
# 投稿ループ
# ----------------------------
def post_loop():
    while True:
        try:
            now = datetime.now()
            future_times = []
            for t in POST_SCHEDULES:
                hour, minute = map(int, t.split(":"))
                # ±7分ランダムずらし
                random_offset = random.randint(-POST_TIME_RANDOM_RANGE, POST_TIME_RANDOM_RANGE)
                candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                candidate += timedelta(minutes=random_offset)
                if candidate <= now:
                    candidate += timedelta(days=1)
                future_times.append(candidate)
            # 次の投稿時刻
            next_time = min(future_times)
            wait_sec = (next_time - now).total_seconds()
            print(f"[POST_LOOP] ⏳ 次の投稿は {next_time.strftime('%H:%M')}（{int(wait_sec//60)}分後）")
            time.sleep(wait_sec)
            print(f"[POST_LOOP] 投稿開始: {datetime.now().strftime('%H:%M')}")
            post_tweet()
        except Exception as e:
            print("[POST_LOOP] 致命的エラー:", e)
            traceback.print_exc()
            time.sleep(600)

# ----------------------------
# サーバ起動 & 投稿スレッド起動
# ----------------------------
@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "x-autobot running!"})

@app.route("/test")
def test():
    post_tweet()
    return jsonify({"result": "ok"})

if __name__ == "__main__":
    print("[MAIN] サービス起動")
    Thread(target=post_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
