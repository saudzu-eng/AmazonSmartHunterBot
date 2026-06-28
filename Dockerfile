FROM python:3.11-slim

WORKDIR /app

# نسخ جميع الملفات دفعة واحدة بما فيها الـ requirements
COPY . .

# تشغيل التثبيت من المجلد الحالي مباشرة
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
