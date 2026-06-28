import os
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# البيانات الصريحة والجاهزة للتشغيل المستقر
TOKEN = "8759675007:AAF6VKC2ra2-PDJcDiNbEAK4HyBlNNDhyN4"

WELCOME_TEXT = (
    "🚀 **مرحباً بك في بوت التسوّق الذكي!**\n\n"
    "• أرسل لي **إسم أي منتج** (مثال: ساعت ذكية، شاشة قيمنق) وسأجلب لك أفضل العروض فوراً.\n"
    "• البوت ينشر أيضاً العروض العامة التلقائية في القناة بانتظام!"
)

# الأزرار السفلية منسقة بشكل متساوي (صفين متطابقين لتجنب تجميد الواجهة)
REPLY_KEYBOARD = [
    ["🔥 عروض يوم برايم", "⚡ عروض بازار"],
    ["💻 الإلكترونيات", "🏠 مستلزمات المنزل"],
    ["👕 الأزياء", "🔍 بحث مخصص"]
]

MARKETING_PHRASES = [
    "✨ **فرصة لا تعوض! المنتج الأكثر حديثاً وتقييماً في أمازون حالياً!**\n\nإذا كنت تبحث عن الجودة العالية، هذا المنتج نال إعجاب المشترين! 😍",
    "🔥 **للباحثين عن التميز والأسعار الذكية الموفرة!**\n\nمنتج رائع وعملي للغاية، يقدم مواصفات ممتازة مقابل السعر. لا تتردد في تصفحه! 👍",
    "🛍️ **صيد اليوم الحصري! لقطة مميزة جداً وتستحق التجربة فوراً.**\n\nمن المنتجات الأعلى مبيعاً وطلباً، مع ميزة الشحن السريع لباب بيتك! 🚚"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # استخدام تنسيق مبسط للأزرار الأساسية لضمان عملها على كل الأجهزة
    reply_markup = ReplyKeyboardMarkup(REPLY_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "🔍 بحث مخصص":
        await update.message.reply_text("🔍 اكتب اسم المنتج الذي تبحث عنه الآن وسأجلب لك رابط العرض فوراً!")
        return

    await update.message.reply_text(f"🔍 جاري قنص أفضل العروض لـ '{user_text}'...")

    product_title = f"{user_text} مميز بأفضل سعر في أمازون السعودية"
    product_image_url = "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png" 
    affiliate_url = "https://www.amazon.sa/dp/B0GGR5SYQC?tag=telegram0e26c-21" 

    chosen_marketing = random.choice(MARKETING_PHRASES)

    caption_text = (
        f"{chosen_marketing}\n\n"
        f"📦 **المنتج:** {product_title}\n\n"
        f"🛒 **الرابط المباشر للعرض:**\n{affiliate_url}"
    )

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 اضغط هنا للانتقال للعرض مباشرة", url=affiliate_url)]
    ])

    try:
        await update.message.reply_photo(
            photo=product_image_url,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )
    except Exception as e:
        # حماية إضافية: إذا رفض تليجرام إرسال الصورة الافتراضية، يرسل النص فوراً لكي لا يتوقف البوت
        await update.message.reply_text(
            caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت يعمل بنظام الأزرار المبسطة...")
    application.run_polling()

if __name__ == "__main__":
    main()
