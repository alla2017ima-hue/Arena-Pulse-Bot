import time
import requests
from bs4 import BeautifulSoup
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
    return "Arena Pulse FilGoal Scraper Bot is active and running 24/7!"

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

# سجل لحفظ العناوين التي نشرت لعدم تكرارها
sent_news = set()

def fetch_filgoal_news():
    """سحب أحدث الأخبار مباشرة من موقع في الجول"""
    global sent_news
    url = "https://www.filgoal.com/"
    
    # ترويسة متصفح حقيقية لمنع الحظر
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن العناوين الرياضية في الموقع (عناوين المقالات والخبر العاجل)
            articles = soup.find_all(['h2', 'h3', 'a'], class_=['title', 'news-title'])
            
            # إذا لم يتم العثور على الكلاسات المحددة، نبحث عن أي روابط تحتوي على عناوين أخبار
            if not articles:
                articles = soup.find_all('a', href=True)
                
            published_count = 0
            for item in articles:
                text = item.get_text().strip()
                # التحقق من أن النص خبر رياضي ذو طول مناسب
                if len(text) > 25 and text not in sent_news:
                    # محاولة استخراج الرابط إن وجد
                    link = item.get('href', '')
                    if link and not link.startswith('http'):
                        link = "https://www.filgoal.com" + link
                    elif not link:
                        link = "https://www.filgoal.com/"
                        
                    sent_news.add(text)
                    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                    
                    message = (
                        f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
                        f"━━━━━━━━━━━━━━━━━━━\n\n"
                        f"
