import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import os
import random

class RockPaperScissorsGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Игра "Камень-Ножницы-Бумага"')
        self.root.geometry('800x720')
        self.root.resizable(False, False)
        
        # Настройка темы и цветов
        self.bg_color = "#2C3E50"
        self.highlight_color = "#3498DB"
        self.text_color = "#ECF0F1"
        self.btn_color = "#E74C3C"
        self.timer_color = "#F39C12"
        
        self.root.configure(bg=self.bg_color)
        
        # Инициализация переменных
        self.countdown = 3
        self.camera = cv2.VideoCapture(0)
        self.choices = ["Камень", "Ножницы", "Бумага"]
        self.player_choice = None
        self.ai_choice = None
        self.game_status = "ready"  # ready, countdown, result
        
        # Определение пути для ресурсов - исправленная версия
        self.resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
        
        # Загрузка изображений
        self.load_images()
        
        # Создание элементов интерфейса
        self.create_widgets()
        
        # Обновление кадра с камеры
        self.frame_update()
    
    def load_images(self):
        try:
            # AI изображение
            ai_path = os.path.join(self.resource_path, "ai.png")
            self.ai_img = Image.open(ai_path)
            self.ai_img = self.ai_img.resize((320, 240))
            self.ai_photo = ImageTk.PhotoImage(self.ai_img)
            
            # Иконка помощи
            help_path = os.path.join(self.resource_path, "help.png")
            self.help_img = Image.open(help_path)
            self.help_img = self.help_img.resize((50, 50))
            self.help_photo = ImageTk.PhotoImage(self.help_img)
            
            # Иконка статистики
            rate_path = os.path.join(self.resource_path, "rate.png")
            self.rate_img = Image.open(rate_path)
            self.rate_img = self.rate_img.resize((50, 50))
            self.rate_photo = ImageTk.PhotoImage(self.rate_img)
            
            print("Изображения интерфейса загружены успешно")
        except Exception as e:
            print(f"Ошибка загрузки изображений интерфейса: {e}")
            # Создаем заглушки для изображений
            self.ai_photo = None
            self.help_photo = None
            self.rate_photo = None
        
        # Загружаем изображения для жестов
        self.gesture_images = {}
        gesture_filenames = {
            "Камень": ["камень.png", "rock.png"],
            "Ножницы": ["ножницы.png", "scissors.png"],
            "Бумага": ["бумага.png", "paper.png"]
        }
        
        for gesture, filenames in gesture_filenames.items():
            loaded = False
            for filename in filenames:
                try:
                    path = os.path.join(self.resource_path, filename)
                    if os.path.exists(path):
                        img = Image.open(path)
                        img = img.resize((100, 100))
                        self.gesture_images[gesture] = ImageTk.PhotoImage(img)
                        print(f"Изображение {filename} загружено успешно")
                        loaded = True
                        break
                except Exception as e:
                    print(f"Не удалось загрузить {filename}: {e}")
            
            if not loaded:
                print(f"Не удалось загрузить изображение для {gesture}, создаем заглушку")
                self.gesture_images[gesture] = None
    
    def create_widgets(self):
        # Создаем фрейм заголовка
        header_frame = tk.Frame(self.root, bg=self.highlight_color, height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text='Игра "Камень-Ножницы-Бумага"', 
                              font=("Arial", 20, "bold"), bg=self.highlight_color, fg=self.text_color)
        title_label.pack(pady=10)
        
        # Основной фрейм для содержимого
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Фрейм для видео и AI
        video_frame = tk.Frame(main_frame, bg=self.bg_color)
        video_frame.pack(fill=tk.X)
        
        # Фрейм для видео с игроком
        player_frame = tk.LabelFrame(video_frame, text="Игрок", font=("Arial", 12), 
                                    bg=self.bg_color, fg=self.text_color, padx=10, pady=10)
        player_frame.grid(row=0, column=0, padx=10)
        
        self.video_label = tk.Label(player_frame, width=320, height=240, bg="black")
        self.video_label.pack()
        
        # Фрейм для ИИ
        ai_frame = tk.LabelFrame(video_frame, text="Компьютер", font=("Arial", 12), 
                               bg=self.bg_color, fg=self.text_color, padx=10, pady=10)
        ai_frame.grid(row=0, column=1, padx=10)
        
        if self.ai_photo:
            self.ai_label = tk.Label(ai_frame, width=320, height=240, image=self.ai_photo, bg="black")
        else:
            self.ai_label = tk.Label(ai_frame, width=320, height=240, text="AI", font=("Arial", 40), 
                                   bg="black", fg="white")
        self.ai_label.pack()
        
        # Фрейм для результатов
        result_frame = tk.Frame(main_frame, bg=self.bg_color, pady=20)
        result_frame.pack(fill=tk.X)
        
        # Выбор игрока
        self.player_choice_frame = tk.LabelFrame(result_frame, text="Ваш выбор", font=("Arial", 12), 
                                              bg=self.bg_color, fg=self.text_color, padx=50, pady=20)
        self.player_choice_frame.grid(row=0, column=0, padx=20)
        
        self.player_choice_label = tk.Label(self.player_choice_frame, text="Ожидание...", 
                                           font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.text_color,
                                           width=10, height=2)
        self.player_choice_label.pack()
        
        self.player_img_label = tk.Label(self.player_choice_frame, bg=self.bg_color)
        self.player_img_label.pack()
        
        # Результат
        self.result_frame = tk.Frame(result_frame, bg=self.bg_color, padx=10, pady=10)
        self.result_frame.grid(row=0, column=1, padx=20)
        
        self.result_label = tk.Label(self.result_frame, text="", font=("Arial", 16, "bold"), 
                                    bg=self.bg_color, fg=self.text_color, width=10, height=2)
        self.result_label.pack()
        
        # Выбор AI
        self.ai_choice_frame = tk.LabelFrame(result_frame, text="Выбор компьютера", font=("Arial", 12), 
                                          bg=self.bg_color, fg=self.text_color, padx=50, pady=20)
        self.ai_choice_frame.grid(row=0, column=2, padx=20)
        
        self.ai_choice_label = tk.Label(self.ai_choice_frame, text="Ожидание...", 
                                       font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.text_color,
                                       width=10, height=2)
        self.ai_choice_label.pack()
        
        self.ai_img_label = tk.Label(self.ai_choice_frame, bg=self.bg_color)
        self.ai_img_label.pack()
        
        # Фрейм для кнопок управления
        control_frame = tk.Frame(main_frame, bg=self.bg_color, pady=20)
        control_frame.pack(fill=tk.X)
        
        self.start_button = tk.Button(control_frame, text="НАЧАТЬ БОЙ", font=("Arial", 14, "bold"), 
                                     bg=self.btn_color, fg=self.text_color, padx=20, pady=10,
                                     command=self.start_game)
        self.start_button.pack()
        
        self.timer_label = tk.Label(main_frame, text="", font=("Arial", 40, "bold"), 
                                   bg=self.bg_color, fg=self.timer_color)
        self.timer_label.pack(pady=10)
        
        # Панель информации
        info_frame = tk.Frame(main_frame, bg=self.bg_color, pady=20)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        if self.help_photo:
            self.help_button = tk.Button(info_frame, image=self.help_photo, bg=self.highlight_color,
                                       command=self.show_help)
        else:
            self.help_button = tk.Button(info_frame, text="?", font=("Arial", 16, "bold"),
                                       bg=self.highlight_color, fg=self.text_color, width=3, height=1,
                                       command=self.show_help)
        self.help_button.grid(row=0, column=0, padx=5)
        
        if self.rate_photo:
            self.stats_button = tk.Button(info_frame, image=self.rate_photo, bg=self.highlight_color,
                                        command=self.show_stats)
        else:
            self.stats_button = tk.Button(info_frame, text="📊", font=("Arial", 16), 
                                        bg=self.highlight_color, fg=self.text_color, width=3, height=1,
                                        command=self.show_stats)
        self.stats_button.grid(row=0, column=1, padx=5)
        
        # Скрытые элементы для справки и статистики
        self.help_text = tk.Text(main_frame, wrap=tk.WORD, width=60, height=10, bg=self.bg_color, 
                               fg=self.text_color, font=("Arial", 12))
        self.help_text.insert(tk.END, """
        Как играть:
        1. Нажмите "НАЧАТЬ БОЙ"
        2. Покажите жест (камень, ножницы или бумагу) перед камерой во время отсчета
        3. Подождите результат
        
        Правила:
        • Камень бьет ножницы
        • Ножницы режут бумагу
        • Бумага покрывает камень
        """)
        self.help_text.config(state=tk.DISABLED)
        
        # Фрейм статистики
        self.stats_frame = tk.Frame(main_frame, bg=self.bg_color)
        
        self.stats_table = ttk.Treeview(self.stats_frame, columns=("wins", "losses", "draws"), 
                                       show="headings", height=5)
        self.stats_table.heading("wins", text="Победы")
        self.stats_table.heading("losses", text="Поражения")
        self.stats_table.heading("draws", text="Ничьи")
        
        self.stats_table.column("wins", width=100)
        self.stats_table.column("losses", width=100)
        self.stats_table.column("draws", width=100)
        
        # Добавим тестовые данные
        self.stats_table.insert("", tk.END, values=("0", "0", "0"))
        
        self.stats_table.pack(fill=tk.BOTH, expand=True)
        
        # Счетчики игр
        self.wins = 0
        self.losses = 0
        self.draws = 0
    
    def frame_update(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  # Отражаем по горизонтали для естественности
            
            # Добавляем рамку если игра активна
            if self.game_status == "countdown":
                cv2.rectangle(frame, (20, 20), (frame.shape[1]-20, frame.shape[0]-20), 
                             (0, 255, 0), 3)
            
            img = Image.fromarray(frame)
            img = img.resize((320, 240))
            imgtk = ImageTk.PhotoImage(img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        else:
            print('Ошибка доступа к камере')
            
        self.root.after(10, self.frame_update)
    
    def start_game(self):
        if self.game_status != "countdown":
            self.game_status = "countdown"
            self.countdown = 3
            self.start_button.config(state=tk.DISABLED)
            self.player_choice_label.config(text="Ожидание...")
            self.ai_choice_label.config(text="Ожидание...")
            self.result_label.config(text="")
            
            # Очистка изображений
            if hasattr(self, 'player_gesture_img'):
                self.player_img_label.config(image="")
            if hasattr(self, 'ai_gesture_img'):
                self.ai_img_label.config(image="")
                
            self.update_countdown()
    
    def update_countdown(self):
        if self.countdown > 0:
            self.timer_label.config(text=str(self.countdown))
            self.countdown -= 1
            self.root.after(1000, self.update_countdown)
        else:
            self.timer_label.config(text="Готово!")
            self.determine_result()
            self.root.after(1000, self.reset_game)
    
    def determine_result(self):
        # В реальном приложении здесь будет обработка распознанного жеста
        # Сейчас просто выбираем случайный жест для демонстрации
        self.player_choice = random.choice(self.choices)
        self.ai_choice = random.choice(self.choices)
        
        self.player_choice_label.config(text=self.player_choice)
        self.ai_choice_label.config(text=self.ai_choice)
        
        # Отображаем изображения жестов, если они доступны
        if self.player_choice in self.gesture_images and self.gesture_images[self.player_choice]:
            self.player_gesture_img = self.gesture_images[self.player_choice]
            self.player_img_label.config(image=self.player_gesture_img)
            
        if self.ai_choice in self.gesture_images and self.gesture_images[self.ai_choice]:
            self.ai_gesture_img = self.gesture_images[self.ai_choice]
            self.ai_img_label.config(image=self.ai_gesture_img)
        
        # Определяем результат
        if self.player_choice == self.ai_choice:
            result = "Ничья!"
            color = "yellow"
            self.draws += 1
        elif ((self.player_choice == "Камень" and self.ai_choice == "Ножницы") or
              (self.player_choice == "Ножницы" and self.ai_choice == "Бумага") or
              (self.player_choice == "Бумага" and self.ai_choice == "Камень")):
            result = "Победа!"
            color = "green"
            self.wins += 1
        else:
            result = "Поражение!"
            color = "red"
            self.losses += 1
        
        self.result_label.config(text=result, fg=color)
        self.game_status = "result"
        
        # Обновляем статистику
        self.stats_table.delete(*self.stats_table.get_children())
        self.stats_table.insert("", tk.END, values=(self.wins, self.losses, self.draws))
    
    def reset_game(self):
        self.start_button.config(state=tk.NORMAL)
        self.timer_label.config(text="")
        
    def show_help(self):
        if self.help_text.winfo_ismapped():
            self.help_text.pack_forget()
        else:
            self.stats_frame.pack_forget()
            self.help_text.pack(pady=20, side=tk.BOTTOM)
    
    def show_stats(self):
        if self.stats_frame.winfo_ismapped():
            self.stats_frame.pack_forget()
        else:
            self.help_text.pack_forget()
            self.stats_frame.pack(pady=20, side=tk.BOTTOM)
    
    def close(self):
        if self.camera.isOpened():
            self.camera.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsGame(root)
    
    def on_close():
        app.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()