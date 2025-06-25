import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "こんにちは。副業について140字でツイートを書いてください"}],
        temperature=0.9,
    )
    print("✅ 生成結果:", response.choices[0].message["content"].strip())
except Exception as e:
    print("❌ エラー:", e)
