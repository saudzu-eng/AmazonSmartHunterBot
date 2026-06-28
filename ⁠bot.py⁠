import re
import os
import sqlite3
import logging
import random
import requests
import urllib.parse
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- إعدادات نظام المراقبة ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- البيانات الخاصة بك ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8759675007:AAF6VKC2ra2-PDJcDiNbEAK4HyBlNNDhyN4")
AMAZON_TRACKING_TAG = os.getenv("AMAZON_TRACKING_TAG", "telegram0e26c-21")
CHANNEL_ID = os.getenv("CHANNEL_ID", "1149146249")

EMERGENCY_ASINS = ["B093X3B4P1", "B0CHWR843K", "B0CVN3CHM7", "B0CMDG96KH"]
DB_FILE = "bot_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_products (
            asin TEXT PRIMARY KEY,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_already_published(asin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM published_products WHERE asin = ?", (asin,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_as_published(asin):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO published_products (asin) VALUES (?)", (asin,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        pass

# --- محرك البحث عن المنتجات بالاسم ---
def search_amazon_products(keyword):
    """البحث في أمازون السعودية بالكلمة المفتاحية وسحب أول 3 منتجات"""
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://www.amazon.sa/s?k={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8"
    }
    
    found_asins = []
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                href = link['href']
                # استخراج الـ ASIN من نتائج البحث
                match = re.search(r'/(dp|product)/([A-Z0-9]{10})', href)
                if match:
                    asin = match.group(2)
                    if asin not in found_asins:
                        found_asins.append(asin)
                if len(found_asins) >= 3: # نكتفي بأفضل 3 خيارات ظهرت في البحث
                    break
    except Exception as e:
        logger.error(f"خطأ أثناء البحث في أمازون: {e}")
    return found_asins

# --- محرك جلب التلقائي (التريند والخصومات) ---
def fetch_trending_asins():
    asins = []
    urls = [
        "https://www.amazon.sa/-/en/gp/bestsellers/electronics/",
        "https://www.amazon.sa/-/en/gp/goldbox"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9"
    }
    session = requests.Session()
    for url in urls:
        try:
            response = session.get(url, headers=headers, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                links = soup.find_all("a", href=True)
                for link in links:
                    href = link['href']
                    match = re.search(r'/(dp|product)/([A-Z0-9]{10})', href)
                    if match:
                        asin = match.group(2)
                        if asin not in asins and not is_already_published(asin):
                            asins.append(asin)
            if len(asins) >= 5:
                break
        except Exception as e:
            continue

    if not asins:
        random.shuffle(EMERGENCY_ASINS)
        for asin in EMERGENCY_ASINS:
            if not is_already_published(asin):
                asins.append(asin)
                break
    return asins

# --- صياغة النص التسويقي الجاذب ---
def generate_marketing_text(asin):
    affiliate_url = f"https://www.amazon.sa/dp/{asin}?tag={AMAZON_TRACKING_TAG}"
    templates = [
        "⭐ **الكل يتكلم عن هذا المنتج في أمازون!** ⭐\n\n"
        "لو كنت تبحث عن الجودة والراحة، هذا المنتج حصل على **أعلى التقييمات** من المشترين الذين جربوه! 😍\n\n"
        "🔥 **لماذا تطلبه الآن؟**\n"
        "• جودة أصلية وممتازة.\n"
        "• الأكثر مبيعاً وطلباً حالياً.\n"
        "• متوفر شحن سريع ومباشر لباب بيتك.\n\n"
        "🛒 **اغتنمه الآن عبر الرابط التالي:**\n{link}",
        
        "🚨 **تنبيه لقطة اليوم! عروض حصرية** 🚨\n\n"
        "أخيراً متوفر بخصم وسعر ممتاز! هذا المنتج يعتبر من الاختيارات الذكية الأكثر طلباً حالياً لتوفير فلوسك وشراء الأصلي. 📉💰\n\n"
        "👇 **اضغط هنا وتفقد السعر الحالي والشراء مباشرة:**\n{link}"
    ]
    return random.choice(templates).format(link=affiliate_url)

# --- معالجة رسائل البحث المرسلة من المستخدم ---
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_keyword = update.message.text.strip()
    
    # حماية: إذا أرسل رابطاً بدلاً من اسم منتج
    if "amazon" in user_keyword or "http" in user_keyword:
        await update.message.reply_text("⚠️ يرجى إرسال اسم المنتج فقط (مثال: شاشة، ساعة) وليس الرابط.")
        return

    await update.message.reply_text(f"🔍 جاري البحث في أمازون السعودية عن أفضل عروض: **{user_keyword}**...")
    
    asins = search_amazon_products(user_keyword)
    
    if asins:
        for asin in asins:
            marketing_message = generate_marketing_text(asin)
            # إرسال الخيارات للمستخدم في الخاص وتلقائياً إلى قناتك المشتركة لزيادة الأرباح
            await update.message.reply_text(marketing_message, parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=marketing_message, parse_mode="Markdown")
            except Exception:
                pass
    else:
        await update.message.reply_text("❌ عذراً، لم أتمكن من العثور على عروض حية لهذا المنتج حالياً. جرب كلمة أخرى.")

# --- وظيفة النشر التلقائي المجدولة ---
async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    available_asins = fetch_trending_asins()
    if not available_asins:
        return
    target_asin = available_asins[0]
    marketing_message = generate_marketing_text(target_asin)
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=marketing_message, parse_mode="Markdown")
        mark_as_published(target_asin)
    except Exception as e:
        logger.error(f"خطأ بالنشر التلقائي: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **مرحباً بك في بوت التسوّق الذكي!**\n\n"
        "• أرسل لي **إسم أي منتج** (مثال: *ساعة ذكية*، *شاشة قيمنق*) وسأجلب لك أفضل العروض فوراً بـروابط عمولتك.\n"
        "• البوت ينشر أيضاً العروض العامة التلقائية في القناة بانتظام!"
    )

if __name__ == '__main__':
    init_db()
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start_command))
    # مستمع ذكي: أي نص يرسله المستخدم يُعتبر كلمة بحث
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
    
    # المجدل الآلي للعروض العامة كل 3 ساعات
    application.job_queue.run_repeating(auto_post_job, interval=10800, first=10)
    
    print("🤖 البوت المطور بالكامل يعمل الآن بنجاح...")
    application.run_polling()
