FROM python:3.11-slim

WORKDIR /app

# نسخ جميع ملفات المشروع إلى مجلد /app الحالي
COPY . /app

# تشغيل التثبيت بالإشارة إلى المسار الكامل للملف لضمان قراءته
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "bot.py"]
