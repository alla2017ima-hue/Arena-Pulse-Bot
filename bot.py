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

# إعداد خادم ويب مصغر لإرضاء منصة Render والبقاء على قيد الحياة 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Multi-Source Newspaper Bot is active and running 24/7!"

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
            print("✅ [تم بنجاح]: تم نشر الخبر الرياضي في القناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# سجل لحفظ العناوين التي تم نشرها لعدم تكرارها
sent_news = set()

# قائمة متعددة من المصادر الرياضية لضمان تدفق الأخبار باستمرار
SPORTS_RSS_SOURCES = [
    "https://www.filgoal.com/rss/news",
    "https://www.kooora.com/default.aspx?r=rss",
    "https://www.yallakora.com/rss/sections",
    "https://www.aljazeera.net/rss/category/sport",
    "https://www.skynewsarabia.com/web/rss/sports"
]

def fetch_live_sports_news():
    """المرور على عدة مصادر رياضية لجلب الأخبار الحية والمضمونة"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_published = 0
    
    for rss_url in SPORTS_RSS_SOURCES:
        try:
            response = requests.get(rss_url, headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    for entry in feed.entries[:2]: # نأخذ أحدث خبرين من كل مصدر نشط
                        news_title = entry.title
                        news_link = entry.link if hasattr(entry, 'link') else rss_url
                        
                        if news_title not in sent_news:
                            sent_news.add(news_title)
                            current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                            
                            # قالب الجريدة الاحترافي
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
                            news_published += 1
                            time.sleep(3)
                            
                            # إذا نشرنا خبرين في هذه الجولة، نكتفي مؤقتاً لئلا نغرق القناة
                            if news_published >= 3:
                                return
        except Exception as e:
            print(f"⚠ [تنبيه في المصدر {rss_url}]:", e)

def bot_loop():
    print("🤖 صحيفة Arena Pulse الرقمية متعددة المصادر تبدأ العمل...")
    
    # فحص وجلب الأخبار فوراً عند التشغيل
    fetch_live_sports_news()
    
    while True:
        # فحص المصادر كل 10 دقائق
        time.sleep(600)
        fetch_live_sports_news()

if __name__ == "__main__":
    # تشغيل خادم فلاسك في الخلفية
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # تشغيل محرك الأخبار
    bot_loop()
