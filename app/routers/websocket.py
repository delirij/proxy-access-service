"""Роутеры для WebSocket-соединений: отслеживание статуса виртуальных машин в реальном времени"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services import UserService
from app.schemas import UserRead
from app.core.database import get_db
from app.core import security
from app.models import VirtualMachine

websocket_router = APIRouter()


class ConnectionManager:
    """Менеджер для управления активными WebSocket-соединениями"""
    def __init__(self):
        # Словарь для хранения сокетов, где ключ - ID пользователя
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Принять новое соединение и добавить в словарь"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Удалить соединение из словаря при отключении клиента"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        """Отправить текстовое сообщение конкретному пользователю по его ID"""
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)


manager = ConnectionManager()

@websocket_router.websocket("/ws/status/{user_id}")
async def ws_status(
    websocket: WebSocket,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт WebSocket для информирования клиента о статусе его ВМ"""
    await manager.connect(websocket, user_id)

    async def send_periodic_status():
        """Фоновая задача для периодической проверки статуса ВМ пользователя"""
        try:
            while True:
                db.expire_all() # Очищаем кэш сессии для свежих данных из БД
                
                query = select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
                result = await db.execute(query)
                vm = result.scalar_one_or_none()

                if vm:
                    status_msg = "connected" if vm.is_active else "error"
                    await manager.send_personal_message(status_msg, user_id)
                else:
                    await manager.send_personal_message("disconnected", user_id)
                
                await asyncio.sleep(5) # Ждем 5 секунд перед следующей отправкой
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    task = asyncio.create_task(send_periodic_status())

    try:
        while True:
            # Ждем сообщение от пользователя
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        # Пользователь закрыл приложение или пропал интернет
        pass
    finally:
        task.cancel() # Останавливаем рассылку при обрыве соединения
        manager.disconnect(user_id)
