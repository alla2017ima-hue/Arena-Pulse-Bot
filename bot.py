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

# قائمة لتتبع آخر المقالات المنشورة لمنع التكرار القريب
sent_news_memory = set()
MAX_MEMORY_SIZE = 150  # الاحتفاظ بآخر 150 عنوان فقط لضمان عدم توقف الدورات

def fetch_and_publish_news():
    """جلب 5 مقالات جديدة في كل دورة ساعية وضمان استمرار العمليات"""
    global sent_news_memory
    print(f"🚀 [الدورة الساعية] جاري بدء فحص وجلب الأخبار الجديدة... الوقت: {datetime.now().strftime('%H:%M')}")
    
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
                    
                    if len(title) > 20 and title not in sent_news_memory:
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
            
    # ترتيب المقالات حسب الأولوية
    all_articles.sort(key=lambda x: x["priority"], reverse=True)
    
    # اختيار 5 مقالات جديدة فعلياً
    final_articles = []
    for art in all_articles:
        if art["title"] not in sent_news_memory:
            final_articles.append(art)
            sent_news_memory.add(art["title"])
            if len(final_articles) == 5:
                break
                
    # تنظيف الذاكرة إذا تجاوزت الحجم الأقصى لكي لا تتوقف الدورات القادمة أبداً
    if len(sent_news_memory) > MAX_MEMORY_SIZE:
        # الاحتفاظ فقط بنصف العناصر الأخيرة
        sent_news_memory = set(list(sent_news_memory)[-75:])
                
    print(f"📊 إجمالي المقالات المختارة للنشر في هذه الدورة: {len(final_articles)} مقالات.")
    
    if not final_articles:
        print("⚠ لم يتم العثور على مقالات جديدة في هذه الساعة، سيتم إعادة المحاولة في الدورة القادمة.")
        return

    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    intro_message = f"📰 *موجز Arena Pulse الساعي*\nأبرز 5 محطات رياضية لهذه الساعة (`{current_time}`)\n━━━━━━━━━━━━━━━━━━━"
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
    """حلقة دورية لا تتوقف أبداً لتشغيل الدورات كل ساعة بدقة (3600 ثانية)"""
    print("⏳ بدأ خيط التشغيل الخلفي (Background Loop) بنجاح...")
    time.sleep(10) # انتظار بسيط عند الإقلاع الأول
    while True:
        try:
            fetch_and_publish_news()
        except Exception as e:
            print(f"❌ حدث خطأ غير متوقع في الدورة: {e}")
            
        print("⏳ انتهت الدورة الحالية. البوت في وضع الانتظار لمدة ساعة كاملة للدورة القادمة...")
        time.sleep(3600)

if __name__ == "__main__":
    # تشغيل سيرفر الويب لاستقرار Render
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    
    # تشغيل حلقة النشر التلقائية المستمرة
    t_loop = threading.Thread(target=background_loop)
    t_loop.daemon = True
    t_loop.start()
    
    # حلقة رئيسية للحفاظ على تشغيل السيرفر
    while True:
        time.sleep(3600)
