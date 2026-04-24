"""Фоновые задачи Celery для асинхронной отправки писем с кодами активации пользователям сервиса"""
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
    message.set_content(f"Твой ключ активации для доступа к прокси: {activation_key}")

    await aiosmtplib.send(
        message, 
        hostname="mailpit",
        port=1025
    )


@shared_task(name="send_activation_email")
def send_message(email: str, activation_key: str):
    asyncio.run(send_message_to_email(email, activation_key))
    return True