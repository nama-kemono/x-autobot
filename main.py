from flask import Flask
from tweet import post_tweet

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Flaskアプリは動作中です"

@app.route("/test")
def test():
    result = post_tweet()
    return "✅ テスト投稿完了" if result else "❌ テスト投稿失敗"

if __name__ == "__main__":
    app.run(debug=True)