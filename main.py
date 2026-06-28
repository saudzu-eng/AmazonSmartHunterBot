import os
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك للتشغيل المباشر
TOKEN = "8759675007:AAF6VKC2ra2-PDJcDiNbEAK4HyBlNNDhyN4"

# معرف التليجرام الخاص بك كمسؤول عن البوت
ADMIN_ID = 1149146249

# كود التسويق بالعمولة الخاص بك
AFFILIATE_TAG = "telegram0e26c-21"

# رسالة الترحيب الاحترافية والمصاغة بأسلوب تسويقي مميز
WELCOME_TEXT = (
    "🚀 **مرحباً بك في منصة التسوّق الذكي وعروض أمازون الحصرية!**\n\n"
    "• اكتشف أقوى التخفيضات اليومية المتجددة عبر تصفح الأقسام بالأسفل.\n"
    "• أو اكتب **إسم أي منتج** تريده مباشرة، وسأقوم بقنص أفضل سعر متوفر بالمعلومات والصور الحقيقية فوراً!"
)

MAIN_KEYBOARD = [
    ["👕 الملابس", "👟 الأحذية"],
    ["💻 الأجهزة الرقمية", "🏠 المنزل والمطبخ"],
    ["💄 الصحة والجمال", "🔍 بحث مخصص"]
]

SUB_KEYBOARDS = {
    "👕 الملابس": [["👔 جميع الملابس", "👕 البلايز والتيشيرتات"], ["🥼 القمصان", "🩳 الشورتات والبناطيل"], ["🔙 العودة للقائمة الرئيسية"]],
    "👟 الأحذية": [["👟 جميع الأحذية", "👟 أحذية السنيكرز"], ["👞 أحذية اللوفر", "🥾 الأحذية الطويلة"], ["🔙 العودة للقائمة الرئيسية"]],
    "💻 الأجهزة الرقمية": [["📱 الجوالات وإكسسواراتها", "💻 أجهزة الكمبيوتر"], ["📺 التلفزيونات والإلكترونيات", "🔌 Kindle و Alexa"], ["🔙 العودة للقائمة الرئيسية"]],
    "🏠 المنزل والمطبخ": [["🏠 المنزل والأثاث", "🍳 المطبخ والأجهزة المنزلية"], ["⛺ مستلزمات الرياضة والتخييم", "🛠️ الأدوات والمعدات"], ["🔙 العودة للقائمة الرئيسية"]],
    "💄 الصحة والجمال": [["💄 المكياج والعناية", "🧼 العناية الشخصية"], ["✨ العطور الحصرية", "💊 الفيتامينات والمكملات"], ["🔙 العودة للقائمة الرئيسية"]]
}

MARKETING_PHRASES = [
    "✨ **فرصة لا تعوض! المنتج الأكثر طلباً وتقييماً في أمازون حالياً!** 😍",
    "🔥 **للباحثين عن التميز والأسعار الذكية الموفرة للجاذبية!** 👍",
    "🛍️ **صيد اليوم الحصري! لقطة مميزة جداً وتستحق التجربة فوراً.** 🚚"
]

AUTO_SEARCH_KEYWORDS = ["ساعة ذكية", "شاشة قيمنق", "سماعات لاسلكية", "ماكينة قهوة", "عطور رجالية", "جوال سامسونج", "حقيبة ظهر"]

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
            return None
        soup = BeautifulSoup(response.content, "html.parser")
        result_card = soup.find("div", {"data-component-type": "s-search-result"})
        if not result_card:
            return None
            
        title = result_card.find("h2", {"class": "a-size-mini"}).text.strip()
        image_url = result_card.find("img", {"class": "s-image"})["src"]
        
        brand_element = result_card.find("span", {"class": "a-size-base-plus a-color-base"})
        brand = brand_element.text.strip() if brand_element else "ماركة مميزة"
        
        description = "خصم ناري حصري لفترة محدودة جداً مع شحن مجاني للمشتركين."
        price_element = result_card.find("span", {"class": "a-price-whole"})
        if price_element:
            description += f" | السعر الحالي: {price_element.text.strip()} ريال سعودي."

        return {"title": title[:90] + "...", "image": image_url, "brand": brand, "description": description, "url": affiliate_url}
    except Exception:
        return None

async def auto_post_deal(context: ContextTypes.DEFAULT_TYPE):
    random_keyword = random.choice(AUTO_SEARCH_KEYWORDS)
    product_data = fetch_amazon_product(random_keyword)
    
    if product_data:
        caption_text = (
            f"📢 **[أقوى العروض الحالية]**\n"
            f"🔥 **صفقة مميزة عثرت عليها المنصة لك الآن!**\n\n"
            f"📦 **اسم المنتج:** {product_data['title']}\n"
            f"🏭 **البراند:** {product_data['brand']}\n"
            f"📝 **التفاصيل:** {product_data['description']}\n\n"
            f"🛒 **تسوق العرض مباشرة شامل الخصم التلقائي:**\n{product_data['url']}"
        )
        inline_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 اضغط هنا للانتقال للعرض مباشرة", url=product_data['url'])]])
        
        try:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=product_data['image'], caption=caption_text, parse_mode="Markdown", reply_markup=inline_keyboard)
        except Exception as e:
            print(f"Failed to auto post: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 **مرحباً بك يا مدير المنصة الموقر!**\n\n" + WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text == "🔙 العودة للقائمة الرئيسية":
        reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        await update.message.reply_text("📋 تم الرجوع إلى قائمة الأقسام الرئيسية:", reply_markup=reply_markup)
        return
    if user_text in SUB_KEYBOARDS:
        reply_markup = ReplyKeyboardMarkup(SUB_KEYBOARDS[user_text], resize_keyboard=True)
        await update.message.reply_text(f"👇 تصفح أقسام **{user_text}** الفرعية المتاحة:", parse_mode="Markdown", reply_markup=reply_markup)
        return
    if user_text == "🔍 بحث مخصص":
        await update.message.reply_text("🔍 اكتب اسم أي منتج تريده بدقة الآن وسأبحث عنه فوراً!")
        return

    status_message = await update.message.reply_text(f"🔄 جاري قنص أفضل العروض لـ '{user_text}'...")
    product_data = fetch_amazon_product(user_text)
    
    if not product_data:
        encoded_query = urllib.parse.quote(user_text)
        product_data = {
            "title": f"{user_text} المميز",
            "image": "https://images-na.ssl-images-amazon.com/images/G/01/amazon-logos/Amazon_Anvil_Logo_Main._CB416246944_.png",
            "brand": "أمازون السعودية",
            "description": "تصفح العروض المتوفرة لهذا المنتج عبر الرابط مباشرة.",
            "url": f"https://www.amazon.sa/s?k={encoded_query}&tag={AFFILIATE_TAG}"
        }

    chosen_marketing = random.choice(MARKETING_PHRASES)
    caption_text = (
        f"{chosen_marketing}\n\n"
        f"📦 **اسم المنتج:** {product_data['title']}\n"
        f"🏭 **الشركة/البراند:** {product_data['brand']}\n"
        f"📝 **الوصف:** {product_data['description']}\n\n"
        f"🛒 **رابط العرض المباشر (شامل خصمك):**\n{product_data['url']}"
    )
    inline_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 اضغط هنا لتصفح العروض مباشرة", url=product_data['url'])]])
    await status_message.delete()

    try:
        await update.message.reply_photo(photo=product_data['image'], caption=caption_text, parse_mode="Markdown", reply_markup=inline_keyboard)
    except Exception:
        await update.message.reply_text(caption_text, parse_mode="Markdown", reply_markup=inline_keyboard)

def main():
    application = Application.builder().token(TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(auto_post_deal, interval=7200, first=10)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت المحدث يعمل الآن بأسلوب ترحيبي احترافي...")
    application.run_polling()

if __name__ == "__main__":
    main()
