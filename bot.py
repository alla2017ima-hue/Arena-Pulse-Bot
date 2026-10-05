import time
import random
import requests
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
            print("✅ [تم بنجاح]: تم نشر التقرير الصحفي في القناة.")
        else:
            print("❌ [خطأ في تليجرام]:", result.get("description"))
    except Exception as e:
        print("⚠ [خطأ في الاتصال]:", e)

# قاعدة بيانات المانشيتات والتقارير الرياضية المتجددة والغنية بالتحليلات
SPORTS_NEWS_BANK = [
    {
        "category": "ميركاتو الحصري ⚽",
        "title": "صراع محتدم بين كبار أندية أوروبا للظفر خدمات الموهبة الصاعدة في الانتقالات الشتوية",
        "details": "تشهد كواليس سوق الانتقالات تحركات مكثفة من عدة أندية كبرى تسعى لتعزيز صفوفها بنجوم شباب قادرين على صنع الفارق في الأدوار الإقصائية."
    },
    {
        "category": "تحليل تكتيكي 📊",
        "title": "قراءة فنية في أساليب الضغط العالي وتحولات اللعب السريعة في البطولات الكبرى",
        "details": "تعتمد الأندية الحديثة بشكل متزايد على الاستحواذ الخانق والضغط العكسي الفوري لمنع المنافس من بناء الهجمة، وهو ما فرض تحديات تكتيكية جديدة على المدربين."
    },
    {
        "category": "كواليس الملاعب 🏟️",
        "title": "استعدادات مكثفة وقرارات حاسمة للأندية الكبرى قبل انطلاق الجولة الحاسمة",
        "details": "تركز الأجهزة الفنية على الجانب البدني والنفسي للاعبين لتجاوز الإرهاق الناتج عن ضغط المباريات المتتالية في مختلف المسابقات المحلية والقارية."
    },
    {
        "category": "أرقام قياسية 📈",
        "title": "نجوم القارة العجوز يواصلون تحطيم الأرقام القياسية وتاريخ جديد يُكتب هذا الموسم",
        "details": "تؤكد الإحصائيات الحالية ارتفاع معدلات التهديف والمنافسة الشرسة على الألقاب الفردية والجماعية مقارنة بالمواسم السابقة."
    },
    {
        "category": "تغطية خاصـة 🌟",
        "title": "نظرة على أداء الأندية العربية والمحلية وطموحات المنافسة على الألقاب الخارجية",
        "details": "تتواصل التحضيرات القوية والجلسات الفنية لدراسة نقاط القوة والضعف للمنافسين بهدف ضمان أفضل تمثيل وتحقيق تطلعات الجماهير."
    }
]

sent_articles = set()

def generate_and_publish_news():
    """توليد ونشر تقرير رياضي احترافي من بنك المحتوى الذكي"""
    global sent_articles
    
    # اختيار خبر غير مكرر
    available_news = [n for n in SPORTS_NEWS_BANK if n["title"] not in sent_articles]
    if not available_news:
        sent_articles.clear()
        available_news = SPORTS_NEWS_BANK
        
    article = random.choice(available_news)
    sent_articles.add(article["title"])
    current_time = datetime.now().strftime('%Y-%m-%d | %H:%M')
    
    message = (
        f"📰 **جريدة نبض الملاعب | ARENA PULSE** ⚽\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔖 **التصنيف:** `{article['category']}`\n"
        f"🚨 **مانشيت عاجل:**\n"
        f"📌 *{article['title']}*\n\n"
        f"📝 **التفاصيل والتحليل:**\n"
        f"{article['details']}\n\n"
        f"🔗 **للمزيد من التغطيات الحصرية:**\n"
        f"[تابع قناة Arena Pulse على تليجرام](https://t.me/ArenaPulse_DZ)\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 الإصدار: `{current_time}`\n"
        f"📢 **تحت رعاية شبكة Arena Pulse الرياضية**\n\n"
        f"👇 *لا تنسوا الاشتراك في القناة ومشاركة التغطية ليصلكم كل جديد!*"
    )
    
    send_telegram_message(message)

def delayed_start():
    """انتظار استقرار الخادم ثم بدء النشر الفوري والمنتظم"""
    time.sleep(5)
    generate_and_publish_news()
    
    while True:
        # إرسال تقرير جديد ومميز كل 30 دقيقة بانتظام تامة
        time.sleep(1800)
        generate_and_publish_news()

if __name__ == "__main__":
    t = threading.Thread(target=delayed_start)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
