import os
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توكن البوت (تأكد من ضبطه في إعدادات Variables في Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")

# رسالة الترحيب المعدلة بدون "بروابط عمولتك"
WELCOME_TEXT = (
    "🚀 **مرحباً بك في بوت التسوّق الذكي!**\n\n"
    "• أرسل لي **إسم أي منتج** (مثال: *ساعة ذكية*، *شاشة قيمنق*) وسأجلب لك أفضل العروض فوراً.\n"
    "• البوت ينشر أيضاً العروض العامة التلقائية في القناة بانتظام!"
)

# الأزرار السفلية المبنية على أقسام image_15.png و image_14.png
REPLY_KEYBOARD = [
    ["🔥 عروض يوم برايم", "⚡ عروض بازار"],
    ["💻 الإلكترونيات", "🏠 مستلزمات المنزل"],
    ["👕 الأزياء", "🔍 بحث مخصص"],
    ["⚙️ الإعدادات"]
]

# قائمة الجمل التسويقية الاحترافية المتغيرة (لمنع التكرار)
MARKETING_PHRASES = [
    "✨ **فرصة لا تعوض! الكل يتحدث عن هذا المنتج في أمازون!**\n\nإذا كنت تبحث عن الجودة والراحة، هذا المنتج حصل على أعلى التقييمات من المشترين! 😍",
    "🔥 **للباحثين عن التميز والأسعار الذكية!**\n\nمنتج رائع وعملي للغاية، وموفر جداً مقارنة بالمواصفات التي يقدمها. لا تتردد في تصفحه! 👍",
    " صيد اليوم! لقطة مميزة وتستحق التجربة.\n\nمن المنتجات الأكثر طلباً ومبيعاً حالياً، وشحنه سريع ومباشر لباب بيتك! 🚚",
    "💡 **ذكاء الاختيار! منتج مميز بتقييمات استثنائية.**\n\nجودة أصلية وممتازة، وخيار مثالي ومناسب جداً للاستخدام اليومي. ألقِ نظرة عليه الآن! ✨"
]

# دالة بدء البوت وعرض الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(REPLY_KEYBOARD, resize_keyboard=True, placeholder="اختر القسم أو اكتب ما تبحث عنه...")
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)

# دالة محاكاة جلب المنتج مع الصورة والنص التسويقي المتغير والأزرار الشفافة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # تجاهل نصوص الأزرار العامة أو التعامل معها كأقسام بحث
    if user_text in ["⚙️ الإعدادات", "🔍 بحث مخصص"]:
        await update.message.reply_text("🛠️ هذه الميزة ستكون متاحة قريباً لتخصيص تجربتك بشكل كامل!")
        return

    # إشعار المستخدم بالبحث
    await update.message.reply_text(f"🔍 جاري البحث عن أفضل عروض لـ '{user_text}'...")

    # --- محاكاة بيانات المنتج المسترجع (هنا يربط البوت مع سكريبت البحث الخاص بك) ---
    product_title = f"{user_text} مميز بأفضل سعر في أمازون"
    
    # رابط صورة افتراضي (تأكد من استبداله برابط الصورة الحقيقي المستخرج من كود البحث الخاص بك)
    product_image_url = "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png" 
    
    # رابط العمول الخاص بك
    affiliate_url = f"https://www.amazon.sa/dp/B0GGR5SYQC?tag=telegram0e26c-21" 

    # اختيار جملة تسويقية عشوائية غير مكررة
    marketing_text = random.choice(MARKETING_PHRASES)

    # تجهيز نص الرسالة الاحترافي
    caption_text = (
        f"{marketing_text}\n\n"
        f"📦 **المنتج:** {product_title}\n\n"
        f"🛒 **اغتنمه الآن عبر الرابط التالي:**\n"
        f"{affiliate_url}"
    )

    # تجهيز زر شفاف (Inline Keyboard) تحت الصورة مباشرة
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 اضغط هنا للانتقال للعرض مباشرة", url=affiliate_url)]
    ])

    # إرسال الصورة مدمجة مع النص التسويقي والأزرار الشفافة
    try:
        await update.message.reply_photo(
            photo=product_image_url,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )
    except Exception as e:
        # حل احتياطي في حال كان رابط الصورة تالفاً أو فشل إرسالها
        await update.message.reply_text(
            caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 صائد أمازون الذكي يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
