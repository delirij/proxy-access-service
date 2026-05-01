"""Интеграционные тесты для проверки работы API-эндпоинтов"""
import pytest
import uuid

from app.core.config import get_settings

settings = get_settings()

# Генерируем уникальные данные, чтобы тесты можно было запускать много раз подряд
test_email = f"test_{uuid.uuid4()}@example.com"
test_password = "strongpassword123"
test_vm_name = f"test-vm-{uuid.uuid4()}"

@pytest.mark.anyio
async def test_register_user(async_client):
    """Тест успешной регистрации пользователя"""
    response = await async_client.post(
        "/api/register",
        json={"email": test_email, "password": test_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_email
    assert "id" in data
    assert data["is_active"] is True

@pytest.mark.anyio
async def test_register_existing_user(async_client):
    """Тест ошибки при регистрации с уже существующим email"""
    response = await async_client.post(
        "/api/register",
        json={"email": test_email, "password": test_password}
    )
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]

@pytest.mark.anyio
async def test_login_user(async_client):
    """Тест авторизации (получения JWT токена)"""
    response = await async_client.post(
        "/api/login",
        data={"username": test_email, "password": test_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.anyio
async def test_admin_create_vm(async_client):
    """Тест создания ВМ админом (проверка защиты ключом)"""
    response = await async_client.post(
        "/api/admin/create_vm",
        headers={"X-Admin-Key": settings.ADMIN_SECRET_KEY},
        json={
            "name": test_vm_name,
            "host": "192.168.0.1",
            "port": 1080,
            "protocol": "socks5"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == test_vm_name