import asyncio

from email.message import EmailMessage
from celery import shared_task
import aiosmtplib

from app.core import get_settings

settings = get_settings()

async def send_message_to_email(email: str, activation_key: str):
    """Функция отправки сообщения на email"""

    message = EmailMessage()
    message["From"] = "root@localhost"
    message["To"] = email
    message["Subject"] = "Твой ключ активации"
    message.set_content(f"Твой ключ активации для регистрации на сервисе: {activation_key}")

    await aiosmtplib.send(
        message, 
        hostname=settings.POSTGRES_HOST,
        port=1025
    )


@shared_task(name="send_acrivarion_email")
def send_message():
    asyncio.run(send_message_to_email())
    return True