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
    return "Arena Pulse Web Scraping Newspaper Bot is active and running 24/7!"

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
            print("✅ [تم بنجاح]: تم نشر الخبر في القناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# سجل لحفظ العناوين لمنع تكرارها
sent_news = set()

def fetch_live_sports_news():
    """جلب الأخبار مباشرة عبر تحليل صفحة الموقع (Web Scraping)"""
    target_url = "https://www.yallakora.com/matches"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'ar-DZ,ar;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن عناصر الأخبار والعناوين في الصفحة
            headlines = soup.find_all(['h2', 'h3', 'a'], class_=['title', 'news-title', 'item-title'])
            
            count = 0
            for item in headlines:
                news_title = item.get_text(strip=True)
                news_link = item.get('href', '')
                
                # التأكد من أن العنوان حقيقي وذو صلة وليس فارغاً
                if len(news_title) > 15 and news_title not in sent_news:
                    if not news_link.startswith('http'):
                        news_link = "https://www.yallakora.com" + news_link
                        
                    sent_news.add(news_title)
                    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                    
                    # قالب الجريدة الرياضية الاحترافي
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
                    
                    if count >= 2: # نشر خبرين كحد أقصى في كل دورة
                        break
            
            if count == 0:
                print("⚠️ تنبيه: لم يتم التقاط عناوين جديدة في هذه الدورة، جارٍ إعادة المحاولة لاحقاً.")
        else:
            print(f"⚠️ تعذر الوصول للموقع، كود الاستجابة: {response.status_code}")
            
    except Exception as e:
        print("⚠ [خطأ في عملية التمشيط]:", e)

def bot_loop():
    print("🤖 محرك التنقيب المباشر لصحيفة Arena Pulse بدأ العمل...")
    
    # فحص وجلب الأخبار فوراً عند التشغيل
    fetch_live_sports_news()
    
    while True:
        # فحص الموقع كل 10 دقائق
        time.sleep(600)
        fetch_live_sports_news()

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot_loop()
