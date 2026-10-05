import time
import random
from datetime import datetime
from flask import Flask
import threading
import os
import requests

# إعدادات البوت ومعرف القناة
BOT_TOKEN = "8587695169:AAEcrrxE4ONNfipP2iJP1O0DuaLizKcNvSg"
CHANNEL_ID = "@ArenaPulse_DZ"

# إعداد خادم ويب مصغر لإرضاء منصة Render والبقاء على قيد الحياة 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Arena Pulse Smart Newspaper Bot is active and running 24/7!"

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
            print("✅ [تم بنجاح]: تم نشر الخبر الصحفي في القناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# بنك أخبار وتقارير رياضية متجددة واحترافية
SPORTS_NEWS_BANK = [
    {
        "title": "استعدادات مكثفة في كواليس الأندية الكبرى لفترة الانتقالات القادمة ومفاجآت نارية في الطريق",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "تحليل فني شامل: أسرار التكتيك الحديث وكيف تطورت أساليب الضغط العالي في دوريات الأبطال",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "تقرير خاص: صراع الميركاتو يشتد بين كبار القارة الأوروبية لضم أبرز المواهب الشابة الصاعدة",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "الكشف عن المواعيد الرسمية للمواجهات الحاسمة والمُرتقبة في الأدوار الإقصائية للبطولات القارية",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "إحصائيات وأرقام قياسية جديدة تُسجل في ملاعب كرة القدم العالمية هذا الموسم",
        "link": "https://t.me/ArenaPulse_DZ"
    },
    {
        "title": "كواليس الغرف المغلقة: القرارات التحكيمية واللوائح الجديدة التي ستدخل جيز التنفيذ قريباً",
        "link": "https://t.me/ArenaPulse_DZ"
    }
]

sent_news = set()

def publish_newspaper_bulletin():
    """نشر أحدث المانشيتات والتقارير الرياضية بشكل دوري ومضمون"""
    global sent_news
    
    # اختيار خبر لم يتم نشره بعد
    available_news = [n for n in SPORTS_NEWS_BANK if n["title"] not in sent_news]
    
    # إذا تم نشر كل الأخبار، نقوم بتفريغ الذاكرة لإعادة التدوير بذكاء
    if not available_news:
        sent_news.clear()
        available_news = SPORTS_NEWS_BANK
        
    news = random.choice(available_news)
    sent_news.add(news["title"])
    
    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    # قالب الجريدة الرياضية الاحترافي الذي طلبته
    message = (
        f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚨 **مانشيت عاجل:**\n"
        f"📌 *{news['title']}*\n\n"
        f"🔗 **للاطلاع على التفاصيل الكاملة:**\n"
        f"[اضغط هنا لقراءة التقرير كاملاً]({news['link']})\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 الإصدار: `{current_time}`\n"
        f"📢 **تحت رعاية شبكة Arena Pulse الرياضية**\n\n"
        f"👇 *لا تنسوا الاشتراك في القناة ومشاركة التغطية ليصلكم كل جديد!*"
    )
    
    send_telegram_message(message)

def bot_loop():
    print("🤖 محرك صحيفة Arena Pulse الذكي يبدأ النشر الفوري...")
    
    # نشر خبر فور التشغيل لتأكيد العمل
    publish_newspaper_bulletin()
    
    while True:
        # النشر بانتظام كل ساعة لتظل القناة نشطة ومليئة بالتقارير الحصرية
        time.sleep(3600)
        publish_newspaper_bulletin()

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot_loop()
