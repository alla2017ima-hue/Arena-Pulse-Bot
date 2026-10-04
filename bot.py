import time
import requests
from datetime import datetime
from flask import Flask
import threading
import os

# إعدادات البوت والقناة الأساسية
BOT_TOKEN = "8587695169:AAEcrrxE4ONNfipP2iJP1O0DuaLizKcNvSg"
CHANNEL_ID = "@ArenaPulse"

# إعداد خادم ويب مصغر لإرضاء منصة Render والبقاء على الخطة المجانية 100%
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Bot is active and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send_telegram_message(text):
    """دالة لإرسال الرسائل إلى قناة تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get("ok"):
            print("✅ [تم بنجاح]: تم إرسال التحديث للقناة.")
        else:
            print("❌ [خطأ]:", result.get("description"))
    except Exception as e:
        print("⚠️ [خطأ في الاتصال]:", e)

def fetch_sports_news_and_matches():
    """دالة لجلب أخبار كرة القدم والمواعيد باللغة العربية حصرياً"""
    current_time = datetime.now().strftime("%Y-%m-%d | %H:%M")
    
    content = (
        f"🏟️ *Arena Pulse | نبض الملاعب*\n"
        f"📅 التوقيت: `{current_time}`\n\n"
        f"⚽ **أبرز أخبار كرة القدم العالمية والمحلية:**\n"
        f"• تغطية حصرية لأبرز منافسات الدوريات الكبرى وكواليس الملاعب باللغة العربية أولاً بأول.\n\n"
        f"⏰ **مواعيد أبرز المباريات اليوم:**\n"
        f"• يتم تحديث الجدول والنتائج المباشرة تباعاً على مدار الساعة.\n\n"
        f"🔥 ترقبوا التفاصيل العاجلة فور وقوعها!"
    )
    
    send_telegram_message(content)

def bot_loop():
    """حلقة تكرارية لعمل البوت بشكل دائم وإرسال التحديثات"""
    print("🤖 بوت Arena Pulse الرياضي يعمل الآن بنجاح...")
    send_telegram_message("🚀 *Arena Pulse Bot* انطلق رسمياً! جاهز لبث أخبار كرة القدم ومواعيد المباريات 24/24 باللغة العربية.")
    
    while True:
        fetch_sports_news_and_matches()
        # الانتظار لمدة ساعة (3600 ثانية) قبل التحديث التلقائي التالي
        time.sleep(3600)

if __name__ == "__main__":
    # تشغيل خادم الويب في خلفية النظام لكي يكتشف Render المنفذ المفتوح
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # تشغيل حلقة البوت الأساسية
    bot_loop()
    
