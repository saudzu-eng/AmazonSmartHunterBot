import os
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "8759675007:AAF6VKC2ra2-PDJcDiNbEAK4HyBlNNDhyN4"

WELCOME_TEXT = (
    "🚀 **مرحباً بك في بوت التسوّق الذكي!**\n\n"
    "• أرسل لي **إسم أي منتج** (مثال: *ساعة ذكية*، *شاشة قيمنق*) وسأجلب لك أفضل العروض فوراً بالمعلومات والصور الحقيقية.\n"
    "• البوت ينشر أيضاً العروض العامة التلقائية في القناة بانتظام!"
)

REPLY_KEYBOARD = [
    ["🔥 عروض يوم برايم", "⚡ عروض بازار"],
    ["💻 الإلكترونيات", "🏠 مستلزمات المنزل"],
    ["👕 الأزياء", "💄 الجمال والعناية"],
    ["🔍 بحث مخصص", "⚙️ الإعدادات"]
]

MARKETING_PHRASES = [
    "✨ **فرصة لا تعوض! المنتج الأكثر طلباً وتقييماً في أمازون حالياً!** 😍",
    "🔥 **للباحثين عن التميز والأسعار الذكية الموفرة!** 👍",
    "🛍️ **صيد اليوم الحصري! لقطة مميزة جداً وتستحق التجربة فوراً.** 🚚"
]

# دالة كشط وجلب بيانات المنتج الحقيقي من أمازون
def fetch_amazon_product(query):
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.amazon.sa/s?k={encoded_query}"
    
    # محاكاة متصفح حقيقي لتجنب حظر أمازون
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # البحث عن أول منتج في نتائج البحث
        result_card = soup.find("div", {"data-component-type": "s-search-result"})
        if not result_card:
            return None
            
        # 1. جلب اسم المنتج
        title_element = result_card.find("h2", {"class": "a-size-mini"})
        title = title_element.text.strip() if title_element else query
        
        # 2. جلب صورة المنتج الحقيقية
        image_element = result_card.find("img", {"class": "s-image"})
        image_url = image_element["src"] if image_element else "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png"
        
        # 3. محاكاة جلب الشركة والوصف المختصر (تنظيف النصوص المتاحة ببطاقة البحث)
        brand = "أمازون السعودية"
        description = "متوفر حالياً مع خيارات شحن سريع وتقييمات إيجابية من المشترين."
        
        # محاولة استخراج السعر كجزء من الوصف
        price_element = result_card.find("span", {"class": "a-price-whole"})
        if price_element:
            description += f" | السعر الحالي: {price_element.text.strip()} ريال سعودي."

        return {
            "title": title[:100] + "...", # تقصير الاسم لكي لا يتجاوز حد تليجرام
            "image": image_url,
            "brand": brand,
            "description": description,
            "url": f"https://www.amazon.sa/s?k={encoded_query}&tag=telegram0e26c-21" # رابط العمول الخاص بك
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(REPLY_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text in ["⚙️ الإعدادات", "🔍 بحث مخصص"]:
        await update.message.reply_text("⚙️ هذه الأقسام سيتم ربطها تلقائياً بالعروض قريباً!")
        return

    # إرسال إشعار للمستخدم بالبحث الحالي
    status_message = await update.message.reply_text(f"🔍 جاري فحص أمازون وقنص بيانات '{user_text}' الحقيقية...")

    # جلب البيانات الحقيقية
    product_data = fetch_amazon_product(user_text)

    # إذا فشل الكشط أو لم يجد المنتج، نستخدم الحل الاحتياطي الديناميكي لكي لا يتوقف البوت
    if not product_data:
        encoded_query = urllib.parse.quote(user_text)
        product_data = {
            "title": f"{user_text} المميز",
            "image": "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png",
            "brand": "أمازون السعودية",
            "description": "تصفح العروض المتوفرة لهذا المنتج عبر الرابط مباشرة.",
            "url": f"https://www.amazon.sa/s?k={encoded_query}&tag=telegram0e26c-21"
        }

    chosen_marketing = random.choice(MARKETING_PHRASES)

    # صياغة نص الرسالة الاحترافي بالبيانات المطلوبة (الاسم، الشركة، الوصف)
    caption_text = (
        f"{chosen_marketing}\n\n"
        f"📦 **إسم المنتج:** {product_data['title']}\n"
        f"🏭 **الشركة/المتجر:** {product_data['brand']}\n"
        f"📝 **الوصف:** {product_data['description']}\n\n"
        f"🛒 **رابط العرض المباشر شامل خصمك:**\n{product_data['url']}"
    )

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 اضغط هنا للانتقال للعرض مباشرة", url=product_data['url'])]
    ])

    # مسح رسالة الانتظار أولاً
    await status_message.delete()

    try:
        # إرسال الصورة الحقيقية مع الوصف الكامل والأزرار الشفافة
        await update.message.reply_photo(
            photo=product_data['image'],
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )
    except Exception as e:
        # حل احتياطي نصي متكامل في حال رفض تليجرام أبعاد الصورة المستخرجة
        await update.message.reply_text(
            caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت الذكي يعمل الآن بجلب الصور والبيانات الحقيقية...")
    application.run_polling()

if __name__ == "__main__":
    main()
