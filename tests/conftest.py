"""Настройки и фикстуры для тестирования API с помощью pytest"""
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

# Добавляем корневую директорию проекта в пути Python, чтобы он нашел модуль app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

@pytest.fixture
def anyio_backend():
    """Определяет бэкенд для асинхронных тестов (asyncio)"""
    return 'asyncio'

@pytest.fixture
async def async_client():
    """Создает асинхронный HTTP-клиент для отправки запросов к приложению без запуска реального сервера"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client