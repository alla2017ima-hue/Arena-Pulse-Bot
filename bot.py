import time
import random
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
    return "Arena Pulse Smart Dual Newspaper Bot is active and running 24/7!"

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
            print("✅ [تم بنجاح]: تم نشر المانشيت الصحفي في القناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# بنك الأخبار والتقارير الرياضية الاحتياطي الذكي والمتجدد لضمان استمرار النشر بلا توقف
BACKUP_SPORTS_NEWS = [
    {
        "title": "كواليس مثيرة: صراع محموم بين الأندية الكبرى لتدعيم الصفوف في الميركاتو المقبل",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "تحليل فني: قراءة في أحدث الخطط التكتيكية وأساليب الضغط العالي في البطولات الأوروبية",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "تقرير حصري: أبرز المواهب الشابة التي خطفت الأنظار وأصبحت محط أنظار كبار القارة",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "حالة ترقب واسعة للإعلان عن المواعيد الرسمية للمواجهات الحاسمة والأدوار الإقصائية",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "أرقام قياسية جديدة تُسجل في ملاعب كرة القدم وتاريخ يكتب من جديد هذا الموسم",
        "link": "https://t.me/ArenaPulse_DZ"
    }
]

sent_news = set()
SPORTS_RSS_SOURCES = [
    "https://www.yallakora.com/rss/sections",
    "https://www.filgoal.com/rss/news",
    "https://www.kooora.com/default.aspx?r=rss"
]

def fetch_and_publish_news():
    """محاولة جلب الأخبار الحية، وإذا تعذر الأمر يتم تفعيل النظام الاحتياطي الذكي فورا"""
    global sent_news
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_sent = False
    
    # محاولة الجلب من المصادر الخارجية أولاً
    for rss_url in SPORTS_RSS_SOURCES:
        try:
            response = requests.get(rss_url, headers=headers, timeout=8)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                if feed.entries:
                    for entry in feed.entries[:1]:
                        news_title = entry.title
                        news_link = entry.link if hasattr(entry, 'link') else rss_url
                        
                        if news_title not in sent_news:
                            sent_news
