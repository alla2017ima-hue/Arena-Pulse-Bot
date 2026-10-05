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

# إعداد خادم ويب لاستقرار Render 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Complete Scraper Bot is active and running 24/7!"

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
        if result.get("ok"):
            print("✅ [تم بنجاح]: تم نشر الخبر في القناة.")
        else:
            print("❌ [خطأ في تيليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

def get_priority_score(title):
    """منح نقاط أولوية للخبر لاختيار المانشيتات الكبرى"""
    score = 1
    t = title.lower()
    if any(k in t for k in ["نهائي", "عاجل", "رسمي", "كأس", "دوري أبطال", "ملعب", "باريس", "برشلونة", "ريال مدريد"]):
        score += 5
    if any(k in t for k in ["هدف", "مباراة", "ترتيب", "تشكيل"]):
        score += 3
    return score

# سجل لمنع تكرار نشر نفس الأخبار أثناء التشغيل المستمر
sent_news = set()

def fetch_and_publish_news():
    """جلب 5 مقالات من 5 مواقع كبرى، فلترتها، ونشرها منفردة ومتسلسلة"""
    global sent_news
    print("🚀 بدء عملية جلب حصاد الأخبار الرياضية...")
    
    # تحديد 5 مصادر رياضية متنوعة
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
                source_count = 0
                
                for a_tag in soup.find_all('a', href=True):
                    title = a_tag.get_text().strip()
                    # تنقية العنوان والتأكد أنه خبر حقيقي وليس مجرد زر أو رابط قصير
                    if len(title) > 25 and '\n' not in title and title not in sent_news:
                        link = a_tag.get('href', '')
                        if link and not link.startswith('http'):
                            link = source["domain"] + link
                        elif not link:
                            link = source["url"]
                            
                        priority = get_priority_score(title)
                        all_articles.append({
                            "title": title,
                            "link": link,
                            "source": source["name"],
                            "priority": priority
                        })
                        sent_news.add(title)
                        source_count += 1
                        if source_count >= 5:  # أخذ 5 مقالات كحد أقصى من كل موقع
                            break
        except Exception as e:
            print(f"⚠ تعذر السحب من {source['name']}: {e}")
            
    if not all_articles:
        print("⚠ لم يتم العثور على أخباد جديدة في هذه الدورة.")
        return

    # ترتيب جميع المقالات حسب الأولوية والأهمية الكبرى
    all_articles.sort(key=lambda x: x["priority"], reverse=True)
    
    # اختيار أهم المقالات للنشر الفوري
    top_articles = all_articles[:15]
    print(f"📊 تم اختيار أفضل {len(top_articles)} خبر رئيسي للنشر.")
    
    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    # إرسال رسالة افتتاحية
    intro_message = f"📰 *شبكة Arena Pulse الرياضية*\nإليكم الموجز الإخباري الحالي (`{current_time}`):\n━━━━━━━━━━━━━━━━━━━"
    send_telegram_message(intro_message)
    time.sleep(2)
    
    # نشر كل خبر منفرد ومستقل عن الآخر مع فاصل زمني (4 ثوانٍ)
    for i, item in enumerate(top_articles, 1):
        message = (
            f"⚽ *خبر ({i}/{len(top_articles)}) - {item['source']}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *{item['title']}*\n\n"
            f"🔗 *التفاصيل الكاملة:*\n"
            f"[اضغط هنا لقراءة المقال]({item['link']})\n\n"
            f"📢 *Arena Pulse | نبض الملاعب*"
        )
        send_telegram_message(message)
        time.sleep(4)

def background_loop():
    """حلقة تشغيل دورية لجلب الأخبار كل فترة زمنية بدون قيود جدول زمني معقد"""
    time.sleep(5)  # انتظار قصير بعد تشغيل السيرفر
    while True:
        fetch_and_publish_news()
        print("⏳ انتهاء دورة الجلب الحالية. الانتظار لدورة التحديث القادمة...")
        time.sleep(1800)  # إعادة الجلب تلقائياً كل 30 دقيقة

if __name__ == "__main__":
    # تشغيل خادم الويب على خيط مستقل لإبقاء الخدمة حية على Render
    t_web = threading.Thread(target=run_flask)
    t_web.daemon = True
    t_web.start()
    
    # تشغيل حلقة الجلب في الخلفية لتجربة العمل الفوري والمستمر
    t_loop = threading.Thread(target=background_loop)
    t_loop.daemon = True
    t_loop.start()
    
    # الحفاظ على تشغيل الملف الرئيسي
    while True:
        time.sleep(3600)
