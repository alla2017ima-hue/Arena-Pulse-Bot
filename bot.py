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

# إعداد خادم ويب مصغر لاستقرار Render 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Debug Scraper Bot is active and running 24/7!"

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

# سجل لمنع تكرار نشر الأخبار
sent_news = set()

def fetch_multi_source_news():
    """سحب الأخبار بمرونة فائقة مع طباعة النتائج في الـ Logs للتشخيص"""
    global sent_news
    
    url = "https://www.filgoal.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }
    
    try:
        print(جارٍ الاتصال بموقع FilGoal لجلب الأخبار...)
        response = requests.get(url, headers=headers, timeout=15)
        print(f"حالة الاتصال (Status Code): {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # البحث عن جميع عناوين الروابط في الصفحة الرئيسية
            links = soup.find_all('a', href=True)
            print(f"تم العثور على {len(links)} رابط في الصفحة.")
            
            published_count = 0
            for a_tag in links:
                title = a_tag.get_text().strip()
                # جعل الشرط أكثر مرونة لالتقاط العناوين الرياضية المتاحة
                if len(title) > 20 and title not in sent_news:
                    link = a_tag.get('href', '')
                    if link and not link.startswith('http'):
                        link = "https://www.filgoal.com" + link
                    elif not link:
                        link = url
                        
                    print(f"✔ تم العثور على خبر صالح: {title[:50]}...")
                    sent_news.add(title)
                    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
                    
                    message = (
                        f"📰 *جريدة نبض الملاعب | ARENA PULSE* ⚽\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"🚨 *مانشيت عاجل (من FilGoal):*\n"
                        f"📌 *{title}*\n\n"
                        f"🔗 *التفاصيل:*\n"
                        f"[اضغط هنا لقراءة الخبر كاملاً]({link})\n\n"
                        f"━━━━━━━━━━━━━━━━━━━\n"
                        f"🕒 الإصدار: `{current_time}`\n"
                        f"📢 *شبكة Arena Pulse الرياضية*"
                    )
                    
                    send_telegram_message(message)
                    published_count += 1
                    time.sleep(3)
                    
                    if published_count >= 1: # نشر خبر واحد للتأكد من عمل النظام فوراً
                        break
        else:
            print(f"⚠ خطأ في الاستجابة من الموقع: {response.status_code}")
    except Exception as e:
        print(f"⚠ خطأ أثناء جلب الأخبار: {e}")

def delayed_start():
    """بدء التشغيل الفوري بعد الإقلاع"""
    time.sleep(3)
    fetch_multi_source_news()
    
    while True:
        time.sleep(1800)
        fetch_multi_source_news()

if __name__ == "__main__":
    t = threading.Thread(target=delayed_start)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
