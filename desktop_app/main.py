import threading
import asyncio
import requests
import logging
import websockets
import customtkinter as ctk

# Настройки подключения к бэкенду
API_URL = "http://localhost:8000/api/activate-key"
WS_URL = "ws://localhost:8000/ws/status/"

# Настройка внешнего вида CustomTkinter
ctk.set_appearance_mode("System")  # Темная/светлая тема берется из системы
ctk.set_default_color_theme("blue")

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProxyConnectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Proxy Access Connector")
        self.geometry("400x380")
        self.resizable(False, False)
        
        self.ws_thread = None
        self.ws_loop = None
        self.is_connected = False
        self.current_ws = None
        
        # UI Элементы
        self.title_label = ctk.CTkLabel(self, text="Подключение к прокси", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        self.key_entry = ctk.CTkEntry(self, placeholder_text="Вставьте ваш ключ", width=300)
        self.key_entry.pack(pady=10)
        
        self.connect_btn = ctk.CTkButton(self, text="Подключиться", command=self.start_connection)
        self.connect_btn.pack(pady=10)
        self.default_btn_color = self.connect_btn.cget("fg_color")
        self.default_hover_color = self.connect_btn.cget("hover_color")
        
        self.status_label = ctk.CTkLabel(self, text="Статус: Отключено", text_color="gray")
        self.status_label.pack(pady=10)
        
        # Фрейм для вывода данных виртуальной машины
        self.info_frame = ctk.CTkFrame(self, width=300, height=120)
        self.info_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.vm_info_label = ctk.CTkLabel(self.info_frame, text="Данные сервера появятся здесь", justify="center")
        self.vm_info_label.pack(pady=30)

    def update_status(self, text, color="white"):
        """Безопасное обновление статуса на экране"""
        self.status_label.configure(text=f"Статус: {text}", text_color=color)

    def enable_button(self):
        """Безопасное включение кнопки после обрыва связи или ошибки"""
        self.connect_btn.configure(state="normal")

    def set_connected_ui(self):
        """Настройка интерфейса для состояния Подключено"""
        self.update_status("Подключено", "#28a745")
        self.is_connected = True
        self.connect_btn.configure(text="Отключиться", fg_color="red", hover_color="darkred", state="normal")

    def set_disconnected_ui(self, status_text, status_color):
        """Сброс интерфейса в начальное состояние (Отключено)"""
        self.update_status(status_text, status_color)
        self.is_connected = False
        self.connect_btn.configure(text="Подключиться", fg_color=self.default_btn_color, hover_color=self.default_hover_color, state="normal")
        self.vm_info_label.configure(text="Данные сервера появятся здесь", text_color="gray")

    def start_connection(self):
        """Обработчик нажатия на кнопку"""
        if self.is_connected:
            self.disconnect_proxy()
            return
            
        key = self.key_entry.get().strip()
        if not key:
            self.update_status("Введите ключ!", "red")
            return
        
        self.update_status("Подключение...", "yellow")
        self.connect_btn.configure(state="disabled")
        
        # Выполняем HTTP запрос в отдельном потоке, чтобы не заморозить UI
        threading.Thread(target=self.activate_key, args=(key,), daemon=True).start()

    def disconnect_proxy(self):
        """Инициализация отключения пользователем"""
        self.update_status("Отключение...", "yellow")
        self.connect_btn.configure(state="disabled")
        if self.current_ws and self.ws_loop:
            asyncio.run_coroutine_threadsafe(self.current_ws.close(), self.ws_loop)

    def activate_key(self, key):
        """Отправка ключа в API и получение данных ВМ"""
        try:
            response = requests.post(API_URL, json={"activate_key": key}, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                user_id = data.get("current_user_id")
                host = data.get("host")
                port = data.get("port")
                protocol = data.get("protocol")
                
                # Обновляем UI с полученными данными
                self.vm_info_label.configure(
                    text=f"Протокол: {protocol.upper()}\nХост: {host}\nПорт: {port}",
                    text_color="#28a745" # Зеленый цвет
                )
                self.update_status("Ключ принят, ожидание сети...", "yellow")
                
                # Запускаем WebSocket для получения статусов в реальном времени
                self.start_websocket(user_id)
            else:
                err_msg = data.get("detail", "Ошибка активации")
                self.update_status(err_msg, "red")
                self.enable_button()
                
        except requests.RequestException:
            self.update_status("Ошибка сети. Бэкенд недоступен.", "red")
            self.enable_button()

    def start_websocket(self, user_id):
        """Запуск фонового потока для WebSockets"""
        self.ws_loop = asyncio.new_event_loop()
        self.ws_thread = threading.Thread(target=self.run_websocket_loop, args=(self.ws_loop, user_id), daemon=True)
        self.ws_thread.start()

    def run_websocket_loop(self, loop, user_id):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_client(user_id))

    async def websocket_client(self, user_id):
        """Подключение к WebSocket FastAPI и ожидание статусов"""
        url = f"{WS_URL}{user_id}"
        try:
            async with websockets.connect(url) as websocket:
                self.current_ws = websocket
                while True:
                    message = await websocket.recv()
                    # Для взаимодействия с UI из другого потока используем .after()
                    if message == "connected":
                        self.after(0, self.set_connected_ui)
                    elif message == "disconnected":
                        self.after(0, self.set_disconnected_ui, "Отключено", "gray")
                    elif message == "no_free_vms":
                        self.after(0, self.set_disconnected_ui, "Все прокси заняты", "red")
                    elif message == "error":
                        self.after(0, self.set_disconnected_ui, "Ошибка сервера", "red")
        except websockets.exceptions.ConnectionClosed:
            # Нормальное отключение со стороны клиента
            self.after(0, self.set_disconnected_ui, "Отключено", "gray")
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            self.after(0, self.set_disconnected_ui, "Соединение потеряно", "red")

if __name__ == "__main__":
    app = ProxyConnectorApp()
    app.mainloop()
