# linebot_app.py
import os
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from scudcard import dcard_search_selenium
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
app.logger.setLevel(logging.INFO)

# 設定 LINE Bot 的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 網頁首頁：表單 + 結果
@app.route("/", methods=['GET'])
def web_index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def web_search():
    results = []
    error = None
    department = request.form.get('department', '')
    app.logger.info("使用者輸入查詢: %s", department)

    if department:
        try:
            results = dcard_search_selenium(department + " 東吳 老師")
            app.logger.info("找到文章數: %d", len(results))
        except Exception as e:
            import traceback
            app.logger.error("搜尋錯誤: %s", str(e))
            app.logger.error(traceback.format_exc())
            error = "搜尋時發生錯誤，請稍後再試。"

    return render_template('index.html', results=results, error=error, department=department)

# LINE Webhook
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        import traceback
        print("LINE 處理錯誤:", e)
        print(traceback.format_exc())
        abort(500)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    try:
        results = dcard_search_selenium(user_input)
    except Exception as e:
        results = []
        print("LINE Bot 搜尋錯誤:", e)

    if not results:
        reply = "找不到相關文章。"
    else:
        reply = "\n\n".join([f"{i+1}. {r['title']}\n🔗 {r['url']}" for i, r in enumerate(results[:5])])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
