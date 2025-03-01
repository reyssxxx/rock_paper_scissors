import flet as ft
import cv2
import base64
import random
from collections import defaultdict
from ai import brawl
from time import sleep
import threading

class RockPaperScissorsGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Камень-Ножницы-Бумага"
        self.page.window_width = 800
        self.page.window_height = 720
        self.page.window_resizable = False
        self.page.theme_mode = ft.ThemeMode.DARK
        
        # Инициализация игры
        self.camera = cv2.VideoCapture(0)
        self.choices = ["Камень", "Ножницы", "Бумага"]
        self.game_status = "ready"
        self.countdown = 3
        self.is_camera_active = True
        
        # Статистика
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.gesture_stats = defaultdict(int)
        self.users = {}
        self.current_user = None
        
        # Элементы интерфейса
        self.create_main_ui()
        self.create_profile_ui()
        
        # Запуск потока для камеры
        self.camera_thread = threading.Thread(target=self.update_camera, daemon=True)
        self.camera_thread.start()

    def create_main_ui(self):
        # Основные элементы
        self.title = ft.Text("Камень-Ножницы-Бумага", size=30, weight=ft.FontWeight.BOLD)
        
        self.player_view = ft.Image(width=320, height=240, border_radius=10)
        self.ai_view = ft.Image(src="assets/ai.png", width=320, height=240, border_radius=10)
        
        self.player_choice = ft.Text("Ожидание...", size=20)
        self.ai_choice = ft.Text("Ожидание...", size=20)
        self.result_text = ft.Text("", size=24, weight=ft.FontWeight.BOLD)
        
        self.start_btn = ft.ElevatedButton(
            "НАЧАТЬ БОЙ", 
            on_click=self.start_game,
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            width=200
        )
        
        self.profile_btn = ft.IconButton(
            icon=ft.icons.PERSON,
            on_click=self.show_profile,
            tooltip="Профиль"
        )
        
        self.timer_text = ft.Text("", size=40)
        
        # Сборка основного интерфейса
        self.main_page = ft.Column([
            ft.Row([self.title, self.profile_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.player_view, self.ai_view], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Column([ft.Text("Ваш выбор:"), self.player_choice]),
                ft.Column([self.result_text]),
                ft.Column([ft.Text("Компьютер:"), self.ai_choice])
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Column([self.start_btn, self.timer_text], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=20)

    def create_profile_ui(self):
        # Элементы профиля
        self.username_field = ft.TextField(label="Логин", width=200)
        self.password_field = ft.TextField(label="Пароль", password=True, width=200)
        
        self.register_btn = ft.ElevatedButton(
            "Зарегистрироваться",
            on_click=self.register_user,
            width=200
        )
        
        self.login_btn = ft.ElevatedButton(
            "Войти",
            on_click=self.login_user,
            width=200
        )
        
        self.stats_text = ft.Text("", size=16)
        self.gesture_stats_text = ft.Text("", size=16)
        
        # Сборка страницы профиля
        self.profile_page = ft.Column([
            ft.Text("Профиль", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    self.username_field,
                    self.password_field,
                    ft.Row([self.register_btn, self.login_btn])
                ]),
                ft.Column([
                    self.stats_text,
                    self.gesture_stats_text
                ], spacing=20)
            ], spacing=40)
        ], visible=False)

        self.page.add(self.main_page, self.profile_page)

    def update_stats_display(self):
        total = self.wins + self.losses + self.draws
        win_rate = (self.wins / total * 100) if total > 0 else 0
        
        stats = (
            f"Победы: {self.wins}\n"
            f"Поражения: {self.losses}\n"
            f"Ничьи: {self.draws}\n"
            f"Всего игр: {total}\n"
            f"Винрейт: {win_rate:.1f}%"
        )
        
        most_common = max(self.gesture_stats, key=self.gesture_stats.get, default="Нет данных")
        gesture_stats = f"Самый частый жест: {most_common}\n"
        for gesture, count in self.gesture_stats.items():
            gesture_stats += f"{gesture}: {count}\n"

        self.stats_text.value = stats
        self.gesture_stats_text.value = gesture_stats
        self.page.update()

    def register_user(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            return
            
        if username in self.users:
            self.page.snack_bar = ft.SnackBar(ft.Text("Пользователь уже существует!"))
            self.page.snack_bar.open = True
        else:
            self.users[username] = password
            self.current_user = username
            self.page.snack_bar = ft.SnackBar(ft.Text("Регистрация успешна!"))
            self.page.snack_bar.open = True
            
        self.page.update()

    def login_user(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if self.users.get(username) == password:
            self.current_user = username
            self.page.snack_bar = ft.SnackBar(ft.Text("Вход выполнен!"))
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Неверные данные!"))
            self.page.snack_bar.open = True
            
        self.page.update()

    def show_profile(self, e):
        self.profile_page.visible = not self.profile_page.visible
        self.main_page.visible = not self.profile_page.visible
        if self.profile_page.visible:
            self.update_stats_display()
        self.page.update()

    def update_camera(self):
        while self.is_camera_active:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.flip(frame, 1)
                if self.game_status == "countdown":
                    cv2.rectangle(frame, (20, 20), (frame.shape[1]-20, frame.shape[0]-20), (0, 255, 0), 3)
                
                _, buffer = cv2.imencode('.jpg', frame)
                self.player_view.src_base64 = base64.b64encode(buffer).decode("utf-8")
                self.page.update()

    def start_game(self, e):
        if self.game_status == "ready":
            self.game_status = "countdown"
            self.start_btn.disabled = True
            self.page.update()
            
            for i in range(3, 0, -1):
                self.timer_text.value = str(i)
                self.page.update()
                sleep(1)
            
            self.timer_text.value = "Готово!"
            self.page.update()
            
            ret, frame = self.camera.read()
            player_choice = brawl(frame)
            ai_choice = random.choice(self.choices)
            
            # Обновление статистики
            if player_choice in self.choices:
                self.gesture_stats[player_choice] += 1
                
                if player_choice == ai_choice:
                    self.draws += 1
                    result = "Ничья!"
                    color = ft.colors.YELLOW
                elif ((player_choice == "Камень" and ai_choice == "Ножницы") or
                      (player_choice == "Ножницы" and ai_choice == "Бумага") or
                      (player_choice == "Бумага" and ai_choice == "Камень")):
                    self.wins += 1
                    result = "Победа!"
                    color = ft.colors.GREEN
                else:
                    self.losses += 1
                    result = "Поражение!"
                    color = ft.colors.RED
            else:
                result = "Ошибка!"
                color = ft.colors.RED

            self.player_choice.value = player_choice
            self.ai_choice.value = ai_choice
            self.result_text.value = result
            self.result_text.color = color
            
            self.game_status = "ready"
            self.start_btn.disabled = False
            self.timer_text.value = ""
            self.page.update()
            self.update_stats_display()

    def close(self):
        self.is_camera_active = False
        self.camera.release()

if __name__ == "__main__":
    ft.app(target=RockPaperScissorsGame, assets_dir="assets")
    root.mainloop()
