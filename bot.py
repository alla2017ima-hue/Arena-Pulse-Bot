import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask
import threading
import os
import re

# إعدادات البوت ومعرف القناة
BOT_TOKEN = "8587695169:AAEcrrxE4ONNfipP2iJP1O0DuaLizKcNvSg"
CHANNEL_ID = "@ArenaPulse_DZ"

# إعداد خادم ويب لاستقرار Render 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Pro Scraper Bot is active and running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send_telegram_message(text):
    """دالة لإرسال الرسائل إلى قناة تليجرام مع تأخير بسيط لتسلسل الرسائل"""
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
            print("❌ [خطأ في تيليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

def clean_and_format_title(title):
    """دالة دقيقة لتنظيف العناوين ومنع تداخل الحروف العربية"""
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'[^\w\s\u0600-\u06FF\-\.\,\؟\!\:\'\"]+', '', title)
    return title

def get_priority_score(title):
    """منح نقاط أولوية للخبر لاختيار المانشيتات الكبرى"""
    score = 1
    t = title.lower()
    if any(k in t for k in ["نهائي", "عاجل", "رسمي", "كأس", "دوري أبطال", "ملعب", "باريس", "برشلونة", "ريال مدريد"]):
        score += 5
    if any(k in t for k in ["هدف", "مباراة", "ترتيب", "تشكيل", "نتيجة"]):
        score += 3
    return score

# ملف محلي لحفظ العناوين المنشورة سابقاً لضمان عدم تكرارها نهائياً حتى لو أعيد تشغيل البوت
HISTORY_FILE = "sent_news_history.txt"

def load_sent_news():
    """تحميل سجل الأخبار السابقة من الملف"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f if line.strip())
        except Exception:
            return set()
    return set()

def save_sent_news_to_file(title):
    """حفظ العنوان الجديد مباشرة في ملف السجل"""
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(title + "\n")
    except Exception as e:
        print(f"⚠ خطأ في حفظ السجل: {e}")

# تحميل السجل عند بدء التشغيل
sent_news = load_sent_news()

def fetch_and_publish_news():
    """جلب 5 مقالات جديدة كلياً وغير منشورة مسبقاً ونشرها كل ساعة"""
    global sent_news
    print("🚀 بدء دورة جلب الموجز الساعي (فحص الأخبار الجديدة)...")
    
    sources = [
        {"name": "FilGoal", "url": "https://www.filgoal.com/", "domain": "https://www.filgoal.com"},
        {"name": "Kooora", "url": "https://www.kooora.com/", "domain": "https://www.kooora.com"},
        {"name": "Yallakora", "url": "https://www.yallakora.com/", "domain": "https://www.yallakora.com"},
        {"name": "BeinSports", "url": "https://www.beinsports.com/ar", "domain": "https://www.beinsports.com"},
        {"name": "Goal", "url": "https://www.goal.com/ar", "domain": "https://www.goal.com"}
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }
    
    all_articles = []
    
    for source in sources:
        try:
            print(f"جاري السحب من موقع: {source['name']}...")
            response = requests.get(source["url"], headers=headers, timeout=12)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for a_tag in soup.find_all('a', href=True):
                    raw_title = a_tag.get_text()
                    title = clean_and_format_title(raw_title)
                    
                    # التحقق من أن العنوان طويل بما يكفي وغير موجود نهائياً في سجل الأخبار السابقة
                    if len(title) > 20 and title not in sent_news:
                        link = a_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = source["domain"] + link
                        elif not link:
                            link = source["url"]
                            
                        priority = get_priority_score(title)
                        article_data = {
                            "title": title,
                            "link": link,
                            "source": source["name"],
                            "priority": priority
                        }
                        
                        all_articles.append(article_data)
                            
        except Exception as e:
            print(f"⚠ تعذر السحب من {source['name']}: {e}")
            
    # ترتيب المقالات حسب الأولوية لاختيار أفضل الأخبار الجديدة
    all_articles.sort(key=lambda x: x["priority"], reverse=True)
    
    # اختيار حتى 5 مقالات فريدة حقاً (غير مكررة)
    final_articles = []
    for art in all_articles:
        if art["title"] not in sent_news:
            final_articles.append(art)
            sent_news.add(art["title"])
            save_sent_news_to_file(art["title"])
            if len(final_articles) == 5:
                break
                
    print(f"📊 إجمالي المقالات الجديدة حقاً المختارة للنشر هذه الساعة: {len(final_articles)} مقالات.")
    
    if not final_articles:
        print("⚠ جميع مقالات المواقع الحالية منشورة مسبقاً، بانتظار تحديث المواقع لأخبار جديدة...")
        return

    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    intro_message = f"📰 *موجز Arena Pulse الساعي*\nأبرز 5 محطات رياضية لهذا الساعة (`{current_time}`)\n━━━━━━━━━━━━━━━━━━━"
    send_telegram_message(intro_message)
    time.sleep(2)
    
    for i, item in enumerate(final_articles, 1):
        message = (
            f"🏅 *خبر ({i}/5) - {item['source']}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *{item['title']}*\n\n"
            f"🔗 *التفاصيل الكاملة:*\n"
            f"[اضغط هنا لقراءة المقال]({item['link']})\n\n"
            f"📢 *Arena Pulse | نبض الملاعب*"
        )
        send_telegram_message(message)
        time.sleep(3)

def background_loop():
    """حلقة دورية لتحديث ونشر 5 مقالات جديدة كل ساعة (3600 ثانية)"""
    time.sleep(5)
    while True:
        fetch_and_publish_news()
        print("⏳ انتهت دورة النشر الساعية. بانتظار دورة الساعة القادمة...")
        time.sleep(3600)

if __name__ == "__main__":
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    
    t_loop = threading.Thread(target=background_loop)
    t_loop.daemon = True
    t_loop.start()
    
    while True:
        time.sleep(3600)
