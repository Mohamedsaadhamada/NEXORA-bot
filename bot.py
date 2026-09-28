import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# ==================== الإعدادات والمفاتيح ====================
TELEGRAM_TOKEN = "8252755338:AAEZYMMS27vNRPOZzP_4-bCRilIclugZbkw"
GEMINI_API_KEY = "AQ.Ab8RN6JMWGkwQytLZjYWeWQnnirJqQosurNjHvIroNwmelZUSA"

# إعداد مكتبة Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# قاموس لتخزين جلسات المحادثة لكل مستخدم حتى يتذكر البوت السياق
chats = {}

# إعداد تسجيل الأخطاء (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==================== الأوامر والوظائف ====================

# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # إنشاء جلسة محادثة جديدة للـ user
    chats[user_id] = client.chats.create(model="gemini-2.5-flash")
    
    welcome_text = (
        f"أهلاً بك يا {update.effective_user.first_name}! 👋\n\n"
        "أنا مساعدك الشخصي المدعوم بـ Gemini. يمكنك إرسال أي سؤال أو رسالة وسأجيبك فوراً!\n\n"
        "لإعادة بدء المحادثة ومسح الذاكرة استخدم الأمر /reset."
    )
    await update.message.reply_text(welcome_text)

# أمر إعادة تعيين الذاكرة /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chats[user_id] = client.chats.create(model="gemini-2.5-flash")
    await update.message.reply_text("تمت إعادة تعيين المحادثة ومسح الذاكرة بنجاح! 🔄")

# التعامل مع الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # إذا لم تكن هناك جلسة سابقة للمستخدم، يتم إنشاؤها
    if user_id not in chats:
        chats[user_id] = client.chats.create(model="gemini-2.5-flash")

    # إظهار حالة "جاري الكتابة..." للمستخدم
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # إرسال الرسالة لـ Gemini والحصول على الرد
        response = chats[user_id].send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك. حاول مرة أخرى لاحقاً.")

# ==================== تشغيل البوت ====================
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # تسجيل الأوامر والرسائل
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("البوت يعمل الآن... اضغط Ctrl+C للإيقاف.")
    app.run_polling()