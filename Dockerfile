FROM python:3.11-slim

# نسخ كافة الملفات مباشرة إلى المجلد الرئيسي للحاوية بدون تعقيد WORKDIR
COPY . .

# تثبيت المكتبات بشكل مباشر
RUN pip install --no-cache-dir python-telegram-bot==21.3 apscheduler==3.10.4 beautifulsoup4==4.12.3 requests==2.32.3

# أمر التشغيل المباشر من المجلد الرئيسي
CMD ["python", "bot.py"]
