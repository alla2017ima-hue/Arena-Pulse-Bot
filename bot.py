import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask
import threading
import os
import re

# إعدادات البوت ومعرف القناة الاحترافية
BOT_TOKEN = "8611102687:AAHSCu50WpkjhGCmzinW1icz9lJJZiD-KgY"

CHANNEL_ID = "@ArenaPulse_DZ"

# إعداد خادم الويب لضمان استقرار التشغيل 24/7 مع UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    print("💡 تم استقبال طلب تنشيط من خدمة المراقبة (UptimeRobot). البوت يعمل بكفاءة!")
    return "Arena Pulse Pro Bot is active, running 24/7, and fully optimized!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send_telegram_message(text):
    """إرسال الرسائل إلى قناة تيليجرام بتنسيق احترافي"""
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
    """تنظيف العناوين ومنع تداخل الحروف لضمان مظهر عربي نقي ومثالي"""
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'[^\w\s\u0600-\u06FF\-\.\,\؟\!\:\'\"]+', '', title)
    return title

def get_priority_score(title):
    """منح نقاط أولوية للخبر لاختيار المانشيتات الكبرى والأحداث الهامة"""
    score = 1
    t = title.lower()
    if any(k in t for k in ["نهائي", "عاجل", "رسمي", "كأس", "دوري أبطال", "ملعب", "باريس", "برشلونة", "ريال مدريد"]):
        score += 5
    if any(k in t for k in ["هدف", "مباراة", "ترتيب", "تشكيل", "نتيجة"]):
        score += 3
    return score

# ذاكرة ذكية لتخزين آخر العناوين ومنع تكرارها نهائياً مع إدارة الحجم تلقائياً
sent_news_memory = set()
MAX_MEMORY_SIZE = 200

def fetch_and_publish_news():
    """عملية السحب، الفلترة، والنشر الاحترافي لـ 5 أخبار جديدة"""
    global sent_news_memory
    print(f"🚀 [الدورة الاحترافية] جاري فحص ومسح المواقع الرياضية... الوقت: {datetime.now().strftime('%Y-%m-%d | %H:%M')}")
    
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
            
    # ترتيب المقالات حسب الأولوية لاختيار الأهم
    all_articles.sort(key=lambda x: x["priority"], reverse=True)
    
    # انتقاء 5 مقالات فريدة حصرياً
    final_articles = []
    for art in all_articles:
        if art["title"] not in sent_news_memory:
            final_articles.append(art)
            sent_news_memory.add(art["title"])
            if len(final_articles) == 5:
                break
                
    # إدارة حجم الذاكرة المؤقتة لمنع الامتلاء الزائد واستمرار العمل للأبد
    if len(sent_news_memory) > MAX_MEMORY_SIZE:
        sent_news_memory = set(list(sent_news_memory)[-100:])
                
    print(f"📊 عدد المقالات المختارة للنشر في هذه الدورة: {len(final_articles)}")
    
    if not final_articles:
        print("⚠ لا توجد أخبار جديدة حالياً، بانتظار الدورة القادمة...")
        return

    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    # رسالة مقدمة الموجز الاحترافية
    intro_message = f"📰 *موجز Arena Pulse الساعي*\nأبرز 5 محطات رياضية لهذا اليوم (`{current_time}`)\n━━━━━━━━━━━━━━━━━━━"
    send_telegram_message(intro_message)
    time.sleep(2)
    
    # نشر الأخبار الخمسة بشكل متسلسل وأنيق
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
    """حلقة التشغيل الأبدي: نشر 5 أخبار كل ساعة تماماً (3600 ثانية) مع الحماية ضد التوقف"""
    print("⏳ بدأ خيط التشغيل المستمر (24/7 Background Loop)...")
    time.sleep(10)
    while True:
        try:
            fetch_and_publish_news()
        except Exception as e:
            print(f"❌ خطأ غير متوقع في الدورة: {e}")
            
        print("⏳ انتهت دورة النشر الحالية. البوت في وضع الاستعداد لمدة ساعة كاملة...")
        time.sleep(3600)  # دورة كل ساعة كاملة بانتظام

if __name__ == "__main__":
    # تشغيل سيرفر الويب لاستقرار Render
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    
    # تشغيل حلقة النشر التلقائية المستمرة في الخلفية
    t_loop = threading.Thread(target=background_loop)
    t_loop.daemon = True
    t_loop.start()
    
    # الحفاظ على تشغيل السيرفر الرئيسي
    while True:
        time.sleep(3600)
