"""Точка входа в приложение FastAPI: конфигурация, middleware и подключение роутеров"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, auth, users, vm, websocket

app = FastAPI(
    title="Proxy Service Access",
    description="Сервис для доступа к прокси"
)

# Настройка CORS для разрешения запросов с внешних фронтенд-приложений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vm.router)
app.include_router(admin.router)
app.include_router(websocket.websocket_router)