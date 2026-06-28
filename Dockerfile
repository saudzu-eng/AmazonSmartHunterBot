FROM python:3.11-slim

WORKDIR /app

# تثبيت المكتبات مباشرة بالأسماء دون الحاجة لملف requirements.txt
RUN pip install --no-cache-dir python-telegram-bot==21.3 apscheduler==3.10.4 beautifulsoup4==4.12.3 requests==2.32.3

# نسخ كود البوت
COPY bot.py /app/

CMD ["python", "bot.py"]
