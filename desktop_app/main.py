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
        
        # UI Элементы
        self.title_label = ctk.CTkLabel(self, text="Подключение к прокси", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(20, 10))
        
        self.key_entry = ctk.CTkEntry(self, placeholder_text="Вставьте ваш ключ", width=300)
        self.key_entry.pack(pady=10)
        
        self.connect_btn = ctk.CTkButton(self, text="Подключиться", command=self.start_connection)
        self.connect_btn.pack(pady=10)
        
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

    def start_connection(self):
        """Обработчик нажатия на кнопку"""
        key = self.key_entry.get().strip()
        if not key:
            self.update_status("Введите ключ!", "red")
            return
        
        self.update_status("Подключение...", "yellow")
        self.connect_btn.configure(state="disabled")
        
        # Выполняем HTTP запрос в отдельном потоке, чтобы не заморозить UI
        threading.Thread(target=self.activate_key, args=(key,), daemon=True).start()

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
                while True:
                    message = await websocket.recv()
                    # Для взаимодействия с UI из другого потока используем .after()
                    if message == "connected":
                        self.after(0, self.update_status, "Подключено", "#28a745")
                    elif message == "disconnected":
                        self.after(0, self.update_status, "Отключено", "gray")
                        self.after(0, self.enable_button)
                    elif message == "no_free_vms":
                        self.after(0, self.update_status, "Все прокси заняты", "red")
                        self.after(0, self.enable_button)
                    elif message == "error":
                        self.after(0, self.update_status, "Ошибка сервера", "red")
                        self.after(0, self.enable_button)
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            self.after(0, self.update_status, "Соединение потеряно", "red")
            self.after(0, self.enable_button)

if __name__ == "__main__":
    app = ProxyConnectorApp()
    app.mainloop()
