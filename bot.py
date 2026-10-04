import time
import requests
import feedparser
from datetime import datetime
from flask import Flask
import threading
import os

# إعدادات البوت ومعرف القناة
BOT_TOKEN = "8587695169:AAEcrrxE4ONNfipP2iJP1O0DuaLizKcNvSg"
CHANNEL_ID = "@ArenaPulse_DZ"

# إعداد خادم ويب مصغر لإرضاء منصة Render والبقاء على الخطة المجانية 100%
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Newspaper Bot is active and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send_telegram_message(text):
    """دالة لإرسال الرسائل إلى قناة تليجرام مع الأزرار التفاعلية إن أمكن"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if not result.get("ok"):
            print("❌ [خطأ في الإرسال]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# تخزين العناوين لمنع تكرارها
sent_news = set()

def fetch_live_sports_news():
    """جلب الأخبار وصياغتها على شكل مانشيت جريدة رياضية احترافية"""
    rss_url = "https://www.kooora.com/default.aspx?r=rss"
    
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:2]: # جلب أحدث خبرين في كل دورة
            news_title = entry.title
            news_link = entry.link
            
            if news_title not in sent_news:
                sent_news.add(news_title)
                current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                
                # صياغة الخبر على شكل قالب جريدة رياضية متكامل
                message = (
                    f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🚨 **مانشيت عاجل:**\n"
                    f"📌 *{news_title}*\n\n"
                    f"🔗 **للاطلاع على التفاصيل الكاملة:**\n"
                    f"[اضغط هنا لقراءة الخبر]({news_link})\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🕒 الإصدار: `{current_time}`\n"
                    f"📢 **تحت رعاية شبكة Arena Pulse الرياضية**\n\n"
                    f"👇 *لا تنسوا الاشتراك في القناة ومشاركة التغطية ليصلكم كل جديد:*\n"
                    f"👉 [شاركنا رأيك في التعليقات وتفاعل مع الخبر!]"
                )
                
                send_telegram_message(message)
                time.sleep(3)
                
    except Exception as e:
        print("⚠️ [خطأ في جلب الأخبار]:", e)

def bot_loop():
    """حلقة العمل المستمرة للبوت"""
    print("🤖 صحيفة Arena Pulse الرقمية تبدأ بث الأخبار الحية...")
    send_telegram_message(
        "🗞️ **إعلان رسمي من إدارة تحرير Arena Pulse**\n\n"
        "أهلاً بكل متابعينا الأفاضل في تغطيتنا الرياضية المستمرة.\n"
        "تم إطلاق النسخة الصحفية المباشرة لنقل كافة الأحداث، الكواليس، والأخبار الكبرى أولاً بأول.\n\n"
        "🔔 *ابقوا في قلب الحدث، واشتركوا وادعموا قناتكم لنستمر!*"
    )
    
    while True:
        fetch_live_sports_news()
        # فحص الأخبار الجديدة كل 20 دقيقة لضمان السرعة والتحديث المستمر
        time.sleep(1200)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot_loop()
