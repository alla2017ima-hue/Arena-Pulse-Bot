import time
import requests
from datetime import datetime

# إعدادات البوت والقناة الأساسية
BOT_TOKEN = "8587695169:AAEcrrxE4ONNfipP2iJP1O0DuaLizKcNvSg"
CHANNEL_ID = "@ArenaPulse"

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
            print("✅ [تم بنجاح]: تم إرسال التحديث للقناة.")
        else:
            print("❌ [خطأ]:", result.get("description"))
    except Exception as e:
        print("⚠️ [خطأ في الاتصال]:", e)

def fetch_sports_news_and_matches():
    """دالة لجلب أخبار كرة القدم والملاعب ومواعيد المباريات باللغة العربية"""
    current_time = datetime.now().strftime("%Y-%m-%d | %H:%M")
    
    # رسالة نموذجية متكاملة (يمكننا ربطها لاحقاً بـ API حقيقي للمباريات والأخبار)
    content = (
        f"🏟️ *Arena Pulse | نبض الملاعب*\n"
        f"📅 التوقيت: `{current_time}`\n\n"
        f"⚽ **أبرز أخبار كرة القدم العالمية والمحلية:**\n"
        f"• تغطية حصرية لأبرز منافسات الدوريات الكبرى وكواليس الملاعب الأوروبية والعربية باللغة العربية أولاً بأول.\n\n"
        f"⏰ **مواعيد أبرز المباريات اليوم:**\n"
        f"• سيتم تحديث جدول المباريات الحية والنتائج المباشرة تباعاً على مدار الساعة.\n\n"
        f"🔥 ترقبوا التفاصيل العاجلة فور وقوعها!"
    )
    
    send_telegram_message(content)

if __name__ == "__main__":
    print("🤖 بوت Arena Pulse الرياضي يعمل الآن بنجاح...")
    
    # رسالة ترحيبية عند التشغيل
    send_telegram_message("🚀 *Arena Pulse Bot* انطلق رسمياً! جاهز لبث أخبار كرة القدم ومواعيد المباريات 24/24 باللغة العربية.")
    
    # حلقة تكرارية لإرسال التحديثات ومواعيد المباريات تلقائياً (مثلاً كل ساعة أو ساعتين: 3600 ثانية)
    while True:
        fetch_sports_news_and_matches()
        # الانتظار لمدة ساعة قبل التحديث التلقائي التالي
        time.sleep(3600)
      
