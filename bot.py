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
    return "Arena Pulse Clean Scraper Bot is active and running 24/7!"

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
    """سحب العناوين الإخبارية الحقيقية والمنظمة فقط من موقع في الجول"""
    global sent_news
    url = "https://www.filgoal.com/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استهداف الروابط التي تمثل عناوين أخبار حقيقية وليست جداول نتائج مباريات
            news_items = []
            for a_tag in soup.find_all('a', href=True):
                title = a_tag.get_text().strip()
                # نتأكد أن النص عبارة عن خبر ذو طول مناسب ولا يحتوي على أرقام نتائج مفككة
                if len(title) > 40 and '\n' not in title and title not in sent_news:
                    # استبعاد النصوص التي تبدو كإعلانات أو قوائم قصيرة
                    if "دوري" in title or "منتخب" in title or "النادي" in title or "الدوري" in title or "الرسمي" in title or "مباريات" in title:
                        link = a_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = "https://www.filgoal.com" + link
                        news_items.append((title, link))
            
            published_count = 0
            for title, link in news_items[:3]:
                if title not in sent_news:
                    sent_news.add(title)
                    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                    
                    # تنسيق نظيف، مضغوط، وخالٍ تماماً من الفراغات المزعجة
                    message = f"📰 *جريدة نبض الملاعب | ARENA PULSE* ⚽\n━━━━━━━━━━━━━━━━━━━\n🚨 *الخبر الرياضي:*\n📌 *{title}*\n\n🔗 *التفاصيل:*\n[اضغط هنا لقراءة الخبر كاملأً الواقع]({link})\n━━━━━━━━━━━━━━━━━━━\n🕒 الإصدار: `{current_time}`\n📢 *شبكة Arena Pulse الرياضية*"
                    
                    send_telegram_message(message)
                    published_count += 1
                    time.sleep(3)
                    
                    if published_count >= 1: # نشر خبر واحد نظيف ومرتب في كل دورة لتجنب الازدحام
                        break
        else:
            print(f"⚠ [خطأ HTTP]: رمز الاستجابة {response.status_code}")
    except Exception as e:
        print(f"⚠ [خطأ في جلب الموقع]: {e}")

def delayed_start():
    """بدء التشغيل وجدولة الفحص المستمر"""
    time.sleep(3)
    fetch_filgoal_news()
    
    while True:
        time.sleep(1800) # فحص كل نصف ساعة
        fetch_filgoal_news()

if __name__ == "__main__":
    t = threading.Thread(target=delayed_start)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
