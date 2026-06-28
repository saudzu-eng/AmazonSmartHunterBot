FROM python:3.11-slim

WORKDIR /app

COPY . .

# تثبيت المكتبات مع ملحقات الأمان المطلوبة للأزرار والاتصال المستقر
RUN pip install --no-cache-dir python-telegram-bot[webhooks]==21.3 cryptography==42.0.5 apscheduler==3.10.4 beautifulsoup4==4.12.3 requests==2.32.3

CMD ["python", "main.py"]
