
import random

def generate_prompt():
    style = random.choice(["satori", "lazy", "buzz"])
    if style == "satori":
        return random.choice([
            "気づいてしまった…楽して稼げる人は、仕組みを作った人だけ。#副業 #GPT",
            "努力が報われないと嘆く前に、報われる仕組みを作ったか考えてみよう。#お小遣い #社畜脱出"
        ])
    elif style == "lazy":
        return random.choice([
            "めんどくさがりでもOK。貼るだけで収益、自動化こそが怠け者の味方。#副業 #ズボラ",
            "「今日も疲れた…」そんな人のために、寝てても回る副業を教えます。#GPT #社畜"
        ])
    else:
        return random.choice([
            "【バズ注意】GPTで自動化したら月収10万突破した話、誰でもできる方法教えます。#副業",
            "バズった投稿には理由がある。キーワードは『自動化』『ズボラ』『お小遣い』。#副業"
        ])
