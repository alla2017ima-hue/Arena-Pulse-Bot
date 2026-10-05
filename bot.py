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
    return "Arena Pulse Live Sports Bot is active and running 24/7!"

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

# مصادر RSS حية ومستقرة ومفتوحة لجلب الأخبار الرياضية العالمية والعربية
SPORTS_RSS_SOURCES = [
    "https://www.aljazeera.net/rss/category/sport",
    "https://www.skynewsarabia.com/web/rss/sports",
    "https://www.kooora.com/default.aspx?r=rss" # تم ترك رابط كورة الاحتياطي ضمن المصادر المتعددة
]

def fetch_live_sports_news():
    """جلب الأخبار الرياضية الحية والمباشرة من المصادر المتاحة"""
    global sent_news
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
                    for entry in feed.entries[:2]:
                        news_title = entry.title
                        news_link = entry.link if hasattr(entry, 'link') else rss_url
                        
                        if news_title not in sent_news:
                            sent_news.add(news_title)
                            current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                            
                            # قالب الجريدة الرياضية الاحترافي الأنيق
                            message = (
                                f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
                                f"━━━━━━━━━━━━━━━━━━━\n\n"
                                f"🚨 **مانشيت عاجل:**\n"
                                f"📌 *{news_title}*\n\n"
                               
