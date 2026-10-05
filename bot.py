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
    return "Arena Pulse Multi-Source Smart Bot is active and running 24/7!"

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

def get_priority_score(title):
    """منح نقاط أولوية للخبر بناءً على أهميته وكونه حینياً"""
    score = 1
    t = title.lower()
    # أخبار النهائيات، المباريات الكبرى والأحداث الحينية تأخذ أعلى أولوية
    if any(k in t for k in ["نهائي", "عاجل", "رسمي", "كأس", "دوري أبطال", "مباراة", "الكلبشات"]):
        score += 5
    if any(k in t for k in ["هدف", "تقدم", "تعادل", "تشكيل"]):
        score += 4
    if any(k in t for k in ["ملخص", "تصريحات", "مدرب"]):
        score += 2
    return score

def fetch_multi_source_news():
    """سحب وتنقية وترتيب الأخبار من عدة مواقع رئيسية حسب الأولوية"""
    global sent_news
    
    # قائمة المواقع الرياضية المستهدفة
    sources = [
        {"name": "FilGoal", "url": "https://www.filgoal.com/", "domain": "https://www.filgoal.com"},
        {"name": "Kooora / أرشيف رياضي", "url": "https://www.kooora.com/", "domain": "https://www.kooora.com"}
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }
    
    all_fetched_items = []
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=12)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    title = a_tag.get_text().strip()
                    # تنقية النصوص والتأكد من أنها عناوين حقيقية خالية من الفراغات المزعجة
                    if len(title) > 35 and '\n' not in title and title not in sent_news:
                        link = a_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = source["domain"] + link
                        elif not link:
                            link = source["url"]
                            
                        priority = get_priority_score(title)
                        all_fetched_items.append({
                            "title": title,
                            "link": link,
                            "source": source["name"],
                            "priority": priority
                        })
        except Exception as e:
            print(f"⚠ [تنبيه في المصدر {source['name']}]: {e}")
            
    # ترتيب الأخبار تنازلياً حسب الأولوية (الأكثر أهمية وحينية أولاً)
    all_fetched_items.sort(key=lambda x: x["priority"], reverse=True)
    
    published_count = 0
    for item in all_fetched_items:
        if item["title"] not in sent_news:
            sent_news.add(item["title"])
            current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
            
            message = (
                f"📰 *جريدة نبض الملاعب | ARENA PULSE* ⚽\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🚨 *مانشيت عاجل (من {item['source']}):*\n"
                f"📌 *{item['title']}*\n\n"
                f"🔗 *التفاصيل الحصرية:*\n"
                f"[اضغط هنا لقراءة الخبر كاملاً]({item['link']})\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🕒 الإصدار: `{current_time}`\n"
                f"📢 *شبكة Arena Pulse الرياضية*"
            )
            
            send_telegram_message(message)
            published_count += 1
            time.sleep(3)
            
            if published_count >= 1: # نشر الخبر الأهم حالياً بدقة
                break

def delayed_start():
    """بدء التشغيل وجدولة الفحص المستمر"""
    time.sleep(3)
    fetch_multi_source_news()
    
    while True:
        time.sleep(1200) # فحص وتحديث الأخبار والترتيب كل 20 دقيقة
        fetch_multi_source_news()

if __name__ == "__main__":
    t = threading.Thread(target=delayed_start)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
