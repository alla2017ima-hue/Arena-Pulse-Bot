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

# إعداد خادم ويب مصغر لإرضاء منصة Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Newspaper Bot is active and running 24/7!"

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
            print("✅ [تم بنجاح]: تم إرسال الخبر للقناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

sent_news = set()

def fetch_live_sports_news():
    """جلب الأخبار الرياضية الحية الموثوقة"""
    # استخدام خلاصة رياضية نشطة ومفتوحة
    rss_url = "https://www.yallakora.com/rss/sections"
    
    try:
        # إضافة User-Agent لكي لا يرفض السيرفر الطلب
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            if feed.entries:
                count = 0
                for entry in feed.entries:
                    if count >= 2: # نشر أحدث خبرين فقط في الدورة الواحدة
                        break
                        
                    news_title = entry.title
                    news_link = entry.link if hasattr(entry, 'link') else "https://www.yallakora.com"
                    
                    if news_title not in sent_news:
                        sent_news.add(news_title)
                        current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                        
                        message = (
                            f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
                            f"━━━━━━━━━━━━━━━━━━━\n\n"
                            f"🚨 **مانشيت عاجل:**\n"
                            f"📌 *{news_title}*\n\n"
                            f"🔗 **للاطلاع على التفاصيل الكاملة:**\n"
                            f"[اضغط هنا لقراءة الخبر كاملاً]({news_link})\n\n"
                            f"━━━━━━━━━━━━━━━━━━━\n"
                            f"🕒 الإصدار: `{current_time}`\n"
                            f"📢 **تحت رعاية شبكة Arena Pulse الرياضية**\n\n"
                            f"👇 *لا تنسوا الاشتراك في القناة ومشاركة التغطية ليصلكم كل جديد!*"
                        )
                        
                        send_telegram_message(message)
                        count += 1
                        time.sleep(3)
            else:
                print("⚠️ تنبيه: لا توجد مداخل في الخلاصة حالياً.")
        else:
            print(f"⚠️ خطأ في الاستجابة من الموقع، الكود: {response.status_code}")
            
    except Exception as e:
        print("⚠️ [خطأ في جلب الأخبار]:", e)

def bot_loop():
    print("🤖 صحيفة Arena Pulse الرقمية تبدأ بث الأخبار الحية...")
    
    # تنفيذ الفحص والجلب فور تشغيل البوت
    fetch_live_sports_news()
    
    while True:
        # الانتظار لمدة 15 دقيقة ثم إعادة الفحص
        time.sleep(900)
        fetch_live_sports_news()

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot_loop()
