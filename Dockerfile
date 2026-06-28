# استخدام نسخة بايثون رسمية ومستقرة
FROM python:3.11-slim

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملفات المشروع
COPY . /app

# تثبيت المكتبات بشكل صحيح ومباشر
RUN pip install --no-cache-dir -r requirements.txt

# أمر تشغيل البوت النهائي
CMD ["python", "bot.py"]
