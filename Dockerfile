FROM python:3.11-slim

WORKDIR /app

# نسخ كافة الملفات إلى المجلد الحالي
COPY . .

# تثبيت المكتبات مباشرة
RUN pip install --no-cache-dir python-telegram-bot==21.3 apscheduler==3.10.4 beautifulsoup4==4.12.3 requests==2.32.3

# أمر التشغيل المباشر والأكيد
CMD ["python", "bot.py"]
