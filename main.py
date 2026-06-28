import os
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك للتشغيل المباشر
TOKEN = "8759675007:AAF6VKC2ra2-PDJcDiNbEAK4HyBlNNDhyN4"

# تم إضافة معرف التليجرام الخاص بك هنا ليتعرف عليك البوت كمسؤول (Admin/Owner)
ADMIN_ID = 1149146249

# كود التسويق بالعمولة الخاص بك
AFFILIATE_TAG = "telegram0e26c-21"

WELCOME_TEXT = (
    "🚀 **مرحباً بك في بوت صائد أمازون الذكي!**\n\n"
    "• تصفح الأقسام بالأسفل للوصول إلى العروض فوراً، أو اكتب اسم أي منتج مباشرة وسأبحث لك عنه بالمعلومات والصور الحقيقية الحصرية!"
)

# القائمة الرئيسية (الأقسام الكبرى)
MAIN_KEYBOARD = [
    ["👕 الملابس", "👟 الأحذية"],
    ["💻 الأجهزة الرقمية", "🏠 المنزل والمطبخ"],
    ["💄 الصحة والجمال", "🔍 بحث مخصص"]
]

# القوائم الفرعية المبنية بدقة من خيارات أمازون الخاصة بك
SUB_KEYBOARDS = {
    "👕 الملابس": [
        ["👔 جميع الملابس", "👕 البلايز والتيشيرتات"],
        ["🥼 القمصان", "🩳 الشورتات والبناطيل"],
        ["🔙 العودة للقائمة الرئيسية"]
    ],
    "👟 الأحذية": [
        ["👟 جميع الأحذية", "👟 أحذية السنيكرز"],
        ["👞 أحذية اللوفر", "🥾 الأحذية الطويلة"],
        ["🔙 العودة للقائمة الرئيسية"]
    ],
    "💻 الأجهزة الرقمية": [
        ["📱 الجوالات وإكسسواراتها", "💻 أجهزة الكمبيوتر"],
        ["📺 التلفزيونات والإلكترونيات", "🔌 Kindle و Alexa"],
        ["🔙 العودة للقائمة الرئيسية"]
    ],
    "🏠 المنزل والمطبخ": [
        ["🏠 المنزل والأثاث", "🍳 المطبخ والأجهزة المنزلية"],
        ["⛺ مستلزمات الرياضة والتخييم", "🛠️ الأدوات والمعدات"],
        ["🔙 العودة للقائمة الرئيسية"]
    ],
    "💄 الصحة والجمال": [
        ["💄 المكياج والعناية", "🧼 العناية الشخصية"],
        ["✨ العطور الحصرية", "💊 الفيتامينات والمكملات"],
        ["🔙 العودة للقائمة الرئيسية"]
    ]
}

MARKETING_PHRASES = [
    "✨ **فرصة لا تعوض! المنتج الأكثر طلباً وتقييماً في أمازون حالياً!** 😍",
    "🔥 **للباحثين عن التميز والأسعار الذكية الموفرة للجاذبية!** 👍",
    "🛍️ **صيد اليوم الحصري! لقطة مميزة جداً وتستحق التجربة فوراً.** 🚚"
]

def fetch_amazon_product(query):
    clean_query = query.replace("👔 ", "").replace("👕 ", "").replace("🥼 ", "").replace("🩳 ", "").replace("👟 ", "").replace("👞 ", "").replace("🥾 ", "").replace("📱 ", "").replace("💻 ", "").replace("📺 ", "").replace("🔌 ", "").replace("🏠 ", "").replace("🍳 ", "").replace("⛺ ", "").replace("🛠️ ", "").replace("💄 ", "").replace("🧼 ", "").replace("✨ ", "").replace("💊 ", "")
    
    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://www.amazon.sa/s?k={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    affiliate_url = f"https://www.amazon.sa/s?k={encoded_query}&tag={AFFILIATE_TAG}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"title": clean_query, "image": "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png", "brand": "أمازون السعودية", "description": "تصفح القسم بالكامل للاطلاع على أقوى الخصومات.", "url": affiliate_url}
            
        soup = BeautifulSoup(response.content, "html.parser")
        result_card = soup.find("div", {"data-component-type": "s-search-result"})
        if not result_card:
            return {"title": clean_query, "image": "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png", "brand": "أمازون السعودية", "description": "تصفح القسم بالكامل للاطلاع على أقوى الخصومات.", "url": affiliate_url}
            
        title_element = result_card.find("h2", {"class": "a-size-mini"})
        title = title_element.text.strip() if title_element else clean_query
        
        image_element = result_card.find("img", {"class": "s-image"})
        image_url = image_element["src"] if image_element else "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png"
        
        brand_element = result_card.find("span", {"class": "a-size-base-plus a-color-base"})
        brand = brand_element.text.strip() if brand_element else "براند موثق في أمازون السعودية"
        
        description = "المنتج متوفر الآن مع خيارات شحن سريع ومجاني للمشتركين."
        price_element = result_card.find("span", {"class": "a-price-whole"})
        if price_element:
            description += f" | السعر الحالي يبدأ من: {price_element.text.strip()} ريال سعودي."

        return {
            "title": title[:90] + "...", 
            "image": image_url,
            "brand": brand,
            "description": description,
            "url": affiliate_url
        }
    except Exception:
        return {"title": clean_query, "image": "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png", "brand": "أمازون السعودية", "description": "تصفح القسم بالكامل للاطلاع على أقوى الخصومات.", "url": affiliate_url}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    
    # تحية خاصة لك عند الضغط على start لأنك الأدمن
    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 **مرحباً بك يا مدير البوت! تم التعرف على حسابك بنجاح.**\n\n" + WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "🔙 العودة للقائمة الرئيسية":
        reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        await update.message.reply_text("📋 تم الرجوع إلى قائمة الأقسام الرئيسية لمتجر أمازون:", reply_markup=reply_markup)
        return

    if user_text in SUB_KEYBOARDS:
        reply_markup = ReplyKeyboardMarkup(SUB_KEYBOARDS[user_text], resize_keyboard=True)
        await update.message.reply_text(f"👇 تصفح أقسام **{user_text}** الفرعية المتاحة الآن:", parse_mode="Markdown", reply_markup=reply_markup)
        return

    if user_text == "🔍 بحث مخصص":
        await update.message.reply_text("🔍 اكتب اسم أي منتج أو براند تريده بدقة الآن، وسأقوم بفحص المتجر لجلب أفضل عرض لك!")
        return

    status_message = await update.message.reply_text(f"🔄 جاري قنص أفضل العروض لـ '{user_text}' بتحديثات أمازون الحية...")

    product_data = fetch_amazon_product(user_text)
    chosen_marketing = random.choice(MARKETING_PHRASES)

    caption_text = (
        f"{chosen_marketing}\n\n"
        f"📦 **اسم المنتج:** {product_data['title']}\n"
        f"🏭 **الشركة/البراند:** {product_data['brand']}\n"
        f"📝 **الوصف:** {product_data['description']}\n\n"
        f"🛒 **رابط العرض المباشر (شامل خصمك التلقائي):**\n"
        f"{product_data['url']}"
    )

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 اضغط هنا لتصفح العروض مباشرة", url=product_data['url'])]
    ])

    await status_message.delete()

    try:
        await update.message.reply_photo(
            photo=product_data['image'],
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )
    except Exception:
        await update.message.reply_text(
            caption_text,
            parse_mode="Markdown",
            reply_markup=inline_keyboard
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت يعمل الآن وتعرف على الـ Admin ID بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
