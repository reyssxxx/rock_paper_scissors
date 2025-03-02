import flet as ft
import cv2
import base64
import random
from ai import brawl
from time import sleep
import threading
import os
import manage as profile 

PATH = os.getcwd().replace('\\', '/')
LOGGED = False
NAME = None

class RockPaperScissorsGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Камень-Ножницы-Бумага"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.on_view_pop = self.on_view_pop
        self.page.on_route_change = self.route_change
        self.camera = cv2.VideoCapture(0)
        self.choices = ["Камень", "Ножницы", "Бумага"]
        self.game_status = "ready"
        self.is_camera_active = True
        self.game_history = []
        self.player_choices = []
        
        # Временное хранилище пользователей
        self.temp_users = {
            "admin": {"password": "admin", "stats": {"wins": 0, "losses": 0, "draws": 0}}
        }
        self.current_user = None
        
        self.create_main_ui()
        self.create_profile_ui()
        self.create_stats_ui()
        
        self.page.views.append(self.main_view)
        self.page.update()
        
        self.camera_thread = threading.Thread(target=self.update_camera, daemon=True)
        self.camera_thread.start()

    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(self.main_view)
        
        if self.page.route == "/stats":
            self.page.views.append(self.stats_view)
        
        if self.page.route == "/profile":
            self.page.views.append(self.profile_view)
        
        self.page.update()

    def create_main_ui(self):
        self.stats_button = ft.IconButton(
            icon=ft.icons.INSERT_CHART_OUTLINED,
            on_click=lambda _: self.page.go("/stats"),
            disabled=True,
            tooltip="Статистика"
        )
        
        self.header = ft.Row(
            controls=[
                ft.Text("Камень-Ножницы-Бумага", size=24, expand=True),
                ft.Row([
                    self.stats_button,
                    ft.IconButton(icon=ft.icons.PERSON, on_click=self.show_profile)
                ])
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Виджеты камеры
        self.player_view = ft.Image(width=400, height=300, border_radius=10, fit=ft.ImageFit.CONTAIN)
        self.ai_view = ft.Image(src=f"{PATH}/assets/ai.png", width=400, height=300, border_radius=10)
        

        # Отображение выбора
        self.player_choice = ft.Image(width=150, height=150, border_radius=10, src=f'{PATH}/assets/пусто.png')
        self.ai_choice = ft.Image(width=150, height=150, border_radius=10, src=f'{PATH}/assets/пусто.png')

        # Центральная панель
        self.timer_text = ft.Text("", size=72)
        self.result_text = ft.Text("", size=24)
        self.start_btn = ft.ElevatedButton("НАЧАТЬ БОЙ", on_click=self.start_game, height=100, width=300)
        self.history = ft.Column([], spacing=10)
        self.main_view = ft.View(
            "/",
            [
                self.header,
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            [
                                ft.Text("Ваша камера:", size=20),
                                self.player_view,
                                ft.Divider(height=10),
                                ft.Text("Ваш выбор:", size=20),
                                self.player_choice
                            ],
                            col={"md": 4},
                            spacing=15
                        ),
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            self.timer_text,
                                            self.result_text,
                                            self.start_btn,
                                            ft.Divider(height=10),
                                            ft.Text("Последние игры:", size=20),
                                            self.history
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=15
                                    ),
                                    height=400
                                )
                            ],
                            col={"md": 4},
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Text("Компьютер:", size=20),
                                self.ai_view,
                                ft.Divider(height=10),
                                ft.Text("Выбор компьютера:", size=20),
                                self.ai_choice
                            ],
                            col={"md": 4},
                            spacing=15
                        )
                    ],
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
            ],
            padding=20,
            spacing=20
        )

    def create_profile_ui(self):
        self.username = ft.TextField(label="Логин", width=400, height=60)
        self.password = ft.TextField(label="Пароль", password=True, width=400, height=60)
        self.auth_message = ft.Text("", color=ft.colors.RED)
        
        self.profile_view = ft.View(
            "/profile",
            [
                ft.AppBar(title=ft.Text("Профиль"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=40),
                            ft.Text("АВТОРИЗАЦИЯ", size=26, weight=ft.FontWeight.W_700),
                            ft.Container(height=20),
                            self.auth_message,
                            self.username,
                            self.password,
                            ft.Container(height=30),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Войти",
                                        on_click=self.login_user,
                                        width=180,
                                        height=45,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                                    ft.ElevatedButton(
                                        "Зарегистрироваться",
                                        on_click=self.reg_user,
                                        width=180,
                                        height=45,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
                                ],
                                spacing=40,
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.BACKGROUND,
                    border_radius=20,
                    width=700,
                    height=500
                )
            ],
            padding=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def create_stats_ui(self):
        self.stats_header = ft.Text("СТАТИСТИКА", size=26, weight=ft.FontWeight.W_700)
        self.total_games = ft.Text("Всего игр: 0")
        self.stats_wins = ft.Text("Побед: 0")
        self.stats_losses = ft.Text("Поражений: 0")
        self.stats_draws = ft.Text("Ничьих: 0")
        self.win_rate = ft.Text("WinRate: 0%")
        self.frequent_choice = ft.Text("Частый выбор: ")
        
                
        self.choice_image = ft.Image(width=100, height=100, border_radius=10, src=f'{PATH}/assets/пусто.png')
        self.session_stats = ft.Text("Игр в этой сессии: 0")
        self.logout_btn = ft.ElevatedButton("Выйти из аккаунта", on_click=self.logout_user)
        
        self.stats_view = ft.View(
            "/stats",
            [
                ft.AppBar(title=ft.Text("Статистика"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=20),
                            self.stats_header,
                            ft.Divider(),
                            self.total_games,
                            self.stats_wins,
                            self.stats_losses,
                            self.stats_draws,
                            self.win_rate,
                            ft.Divider(),
                            ft.Row([self.frequent_choice, self.choice_image], 
                                  alignment=ft.MainAxisAlignment.CENTER),
                            ft.Divider(),
                            self.session_stats,
                            ft.Container(height=20),
                            self.logout_btn
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                    bgcolor=ft.colors.BACKGROUND,
                    border_radius=20,
                    width=700,
                )
            ],
            padding=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def update_history(self):
        self.history.controls = []
        for result in self.game_history[-5:]:
            color = ft.colors.GREEN if result == "Победа" else ft.colors.RED if result == "Поражение" else ft.colors.YELLOW
            self.history.controls.append(ft.Text(result, color=color))
        while len(self.history.controls) < 5:
            self.history.controls.append(ft.Text("-", color=ft.colors.GREY))
        self.page.update()

    def update_stats(self):
        if self.current_user:
            stats = profile.get_stat(NAME)
            total = stats['wins'] + stats['loses'] + stats['draws']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            
            
            stats = profile.get_stat(NAME)
            choice = list(stats.values())
            choice = max(choice[2:])
            for key, val in stats.items():
                if val == choice:
                    if key=='rocks':
                        choice='камень'
                    elif key=='scissors':
                        choice='ножницы'
                    if key=='paper':
                        choice='бумага'
            
            self.choice_image.src = f"{PATH}/assets/{choice}.png"
            self.frequent_choice.value = f"Частый выбор: {choice.title()}"
            
            
            self.total_games.value = f"Всего игр: {total}"
            self.stats_wins.value = f"Побед: {stats['wins']}"
            self.stats_losses.value = f"Поражений: {stats['loses']}"
            self.stats_draws.value = f"Ничьих: {stats['draws']}"
            self.win_rate.value = f"WinRate: {win_rate:.1f}%"
            self.session_stats.value = f"Игр в этой сессии: {len(self.game_history)}"
            self.page.update()

    def start_game(self, e):
        if self.game_status != "ready":
            return
            
        self.game_status = "countdown"
        self.start_btn.disabled = True
        
        for i in range(3, 0, -1):
            self.timer_text.value = str(i)
            self.page.update()
            sleep(1)
            
        ret, frame = self.camera.read()
        player_choice = brawl(frame)
        ai_choice = random.choice(self.choices)
        
        if player_choice in self.choices:
            self.player_choices.append(player_choice)
        
        self.player_choice.src = f"{PATH}/assets/{player_choice.lower()}.png" if player_choice in self.choices else ""
        self.ai_choice.src = f"{PATH}/assets/{ai_choice.lower()}.png"
        
        result = "Ошибка"
        if player_choice in self.choices:
            if player_choice == ai_choice:
                result = "Ничья"
                if self.current_user:
                    profile.reg_game('draws', player_choice, NAME)
            elif (player_choice == "Камень" and ai_choice == "Ножницы") or \
                 (player_choice == "Ножницы" and ai_choice == "Бумага") or \
                 (player_choice == "Бумага" and ai_choice == "Камень"):
                result = "Победа"
                if self.current_user:
                    profile.reg_game('wins', player_choice, NAME)
            else:
                result = "Поражение"
                if self.current_user:
                    profile.reg_game('loses', player_choice, NAME)
        
        self.game_history.append(result)
        self.update_history()
        self.update_stats()
        
        self.result_text.value = result
        self.result_text.color = ft.colors.GREEN if result == "Победа" else \
                                ft.colors.RED if result == "Поражение" else \
                                ft.colors.YELLOW
        self.timer_text.value = ""
        self.game_status = "ready"
        self.start_btn.disabled = False
        self.page.update()

    def show_profile(self, e):
        if self.current_user:
            self.page.go("/stats")
        else:
            self.page.go("/profile")

    def login_user(self, e):
        global LOGGED
        global NAME
        username = self.username.value
        password = self.password.value
        
        if profile.login(username, password):
            self.current_user = username
            self.auth_message.value = ""
            self.stats_button.disabled = False
            LOGGED = True
            NAME = username
            self.page.go("/stats")
            self.update_stats()
            self.update_header()
        else:
            self.auth_message.value = "Неверный логин или пароль!"
            self.page.update()

    def reg_user(self, e):
        global LOGGED
        global NAME
        username = self.username.value
        password = self.password.value
        
        if profile.registration(username, password):
            self.current_user = username
            self.auth_message.value = ""
            self.stats_button.disabled = False
            LOGGED = True
            NAME = username
            self.page.go("/stats")
            self.update_stats()
            self.update_header()
        else:
            self.auth_message.value = "Имя уже занято!"
            self.page.update()

    def logout_user(self, e):
        global LOGGED
        global NAME
        LOGGED = False
        NAME = None
        self.current_user = None
        self.stats_button.disabled = True
        self.page.go("/")
        self.update_header()
        self.page.go("/")

    def update_header(self):
        if self.current_user:
            self.header.controls[1].controls[1] = ft.Text(f"👤 {self.current_user}", size=18)
        else:
            self.header.controls[1].controls[1] = ft.IconButton(
                icon=ft.icons.PERSON, 
                on_click=self.show_profile
            )
        self.page.update()

    def update_camera(self):
        while self.is_camera_active:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.flip(frame, 1)
                _, buffer = cv2.imencode('.jpg', frame)
                self.player_view.src_base64 = base64.b64encode(buffer).decode()
                self.page.update()

    def on_view_pop(self, view):
        self.page.views.pop()
        self.page.go(self.page.views[-1].route)

    def close(self):
        self.is_camera_active = False
        self.camera.release()

if __name__ == "__main__":
    ft.app(target=RockPaperScissorsGame, assets_dir="assets")
