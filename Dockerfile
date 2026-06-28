FROM python:3.11-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ جميع ملفات المشروع الحالية (بما فيها bot.py) إلى مجلد العمل
COPY . /app

# تثبيت المكتبات مباشرة بشكل صريح لضمان عدم الاعتماد على أي ملفات خارجية
RUN pip install --no-cache-dir python-telegram-bot==21.3 apscheduler==3.10.4 beautifulsoup4==4.12.3 requests==2.32.3

# أمر تشغيل البوت المباشر
CMD ["python", "bot.py"]
