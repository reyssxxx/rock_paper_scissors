import flet as ft
import cv2
import base64
import random
from collections import defaultdict
from ai import brawl
from time import sleep
import threading

class RockPaperScissorsUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_window()
        self.init_game()
        self.create_interface()
        self.start_camera()

    def setup_window(self):
        self.page.title = "Rock Paper Scissors"
        self.page.window_full_screen = True
        self.page.window_resizable = False
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK

    def init_game(self):
        self.camera = cv2.VideoCapture(0)
        self.choices = ["Камень", "Ножницы", "Бумага"]
        self.game_status = "ready"
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.last_games = []
        self.is_camera_active = True
        self.current_user = "Гость"
        self.gesture_stats = defaultdict(int)

    def create_interface(self):
        # Заголовок
        header = ft.Row(
            controls=[
                ft.IconButton(icon=ft.icons.SUPPORT, tooltip="Поддержка"),
                ft.Text("Камень-Ножницы-Бумага", size=24, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.icons.LEADERBOARD, tooltip="Лидерборд"),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Основные элементы
        self.player_cam = ft.Image(width=400, height=300, border_radius=10)
        self.ai_image = ft.Image(src="assets/ai.png", width=400, height=300, border_radius=10)
        
        self.player_choice_display = ft.Text("Ожидание...", size=18)
        self.ai_choice_display = ft.Text("Ожидание...", size=18)
        
        self.timer_display = ft.Text("", size=40)
        self.result_display = ft.Text("", size=24)
        
        self.start_btn = ft.ElevatedButton(
            "НАЧАТЬ БОЙ",
            icon=ft.icons.PLAY_ARROW,
            width=200,
            height=50,
            on_click=self.start_game
        )

        # История игр
        self.game_history = ft.Column(
            [ft.Text(f"Игра {i+1}: -", size=14) for i in range(5)],
            spacing=5
        )

        # Профиль
        self.profile_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PERSON),
                ft.Text(self.current_user),
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    on_click=self.show_profile,
                    tooltip="Профиль"
                )
            ], spacing=10),
            padding=10,
            right=20,
            bottom=20,
            bgcolor=ft.colors.BLUE_GREY_800,
            border_radius=10
        )

        # Сборка интерфейса
        main_layout = ft.Row(
            [
                ft.Column([
                    ft.Text("Камера игрока:", size=18),
                    self.player_cam,
                    ft.Text("Ваш выбор:", size=18),
                    self.player_choice_display
                ], spacing=10),
                
                ft.Column([
                    ft.Container(height=50),
                    self.timer_display,
                    self.result_display,
                    self.start_btn,
                    ft.Text("Последние игры:", size=18),
                    self.game_history
                ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                
                ft.Column([
                    ft.Text("Компьютер:", size=18),
                    self.ai_image,
                    ft.Text("Выбор компьютера:", size=18),
                    self.ai_choice_display
                ], spacing=10)
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )

        self.page.add(ft.Stack([ft.Column([header, main_layout]), self.profile_btn]))

    def start_camera(self):
        def update_frame():
            while self.is_camera_active:
                ret, frame = self.camera.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    if self.game_status == "countdown":
                        cv2.rectangle(frame, (20, 20), (frame.shape[1]-20, frame.shape[0]-20), (0, 255, 0), 3)
                    _, buffer = cv2.imencode('.jpg', frame)
                    self.player_cam.src_base64 = base64.b64encode(buffer).decode()
                    self.page.update()
                sleep(0.03)
        
        threading.Thread(target=update_frame, daemon=True).start()

    def start_game(self, e):
        if self.game_status == "ready":
            self.game_status = "countdown"
            self.start_btn.disabled = True
            self.reset_display()
            self.countdown_animation()
            
            # Получение выбора игрока
            ret, frame = self.camera.read()
            player_choice = brawl(frame)
            ai_choice = random.choice(self.choices)
            
            # Обновление интерфейса
            self.update_choices(player_choice, ai_choice)
            self.update_game_result(player_choice, ai_choice)
            self.update_history()
            self.reset_game_state()

    def reset_display(self):
        self.player_choice_display.value = "Ожидание..."
        self.ai_choice_display.value = "Ожидание..."
        self.result_display.value = ""
        self.page.update()

    def countdown_animation(self):
        for i in range(3, 0, -1):
            self.timer_display.value = str(i)
            self.page.update()
            sleep(1)
        self.timer_display.value = "Готово!"
        self.page.update()
        sleep(1)
        self.timer_display.value = ""

    def update_choices(self, player, ai):
        self.player_choice_display.value = player if player in self.choices else "Ошибка"
        self.ai_choice_display.value = ai
        self.page.update()

    def update_game_result(self, player, ai):
        if player not in self.choices:
            self.result_display.value = "Ошибка распознавания!"
            self.result_display.color = ft.colors.RED
            return
            
        self.gesture_stats[player] += 1
        
        if player == ai:
            result = "Ничья!"
            color = ft.colors.YELLOW
            self.draws += 1
        elif (player == "Камень" and ai == "Ножницы") or \
             (player == "Ножницы" and ai == "Бумага") or \
             (player == "Бумага" and ai == "Камень"):
            result = "Победа!"
            color = ft.colors.GREEN
            self.wins += 1
        else:
            result = "Поражение!"
            color = ft.colors.RED
            self.losses += 1
        
        self.result_display.value = result
        self.result_display.color = color
        self.page.update()

    def update_history(self):
        result = self.result_display.value
        self.last_games = (self.last_games + [result])[-5:]
        
        for i, text in enumerate(self.game_history.controls):
            if i < len(self.last_games):
                text.value = f"{self.last_games[i]}"
            else:
                text.value = f" "
        self.page.update()

    def reset_game_state(self):
        self.game_status = "ready"
        self.start_btn.disabled = False
        self.page.update()

    def show_profile(self, e):
        # Реализация окна профиля
        profile_dialog = ft.AlertDialog(
            title=ft.Text("Профиль"),
            content=ft.Column([
                ft.Text(f"Игрок: {self.current_user}"),
                ft.Text(f"Победы: {self.wins}"),
                ft.Text(f"Поражения: {self.losses}"),
                ft.Text(f"Ничьи: {self.draws}"),
                ft.Text(f"Самый частый жест: {max(self.gesture_stats, key=self.gesture_stats.get, default='-')}")
            ], spacing=10),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: self.close_dialog())]
        )
        self.page.dialog = profile_dialog
        profile_dialog.open = True
        self.page.update()

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def close(self):
        self.is_camera_active = False
        self.camera.release()

if __name__ == "__main__":
    ft.app(target=RockPaperScissorsUI, assets_dir="assets")
