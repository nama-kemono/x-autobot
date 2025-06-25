from flask import Flask
import os
from datetime import datetime
from tweet import post_tweet

app = Flask(__name__)

@app.route("/")
def index():
    return "X AutoBot is running."

@app.route("/test")
def test():
    result = post_tweet()
    return f"✅ テスト投稿完了: {result}"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)