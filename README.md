# rock-scissors-paper
Всем привет, это команда "За час до дедлайна". Мы представляем вам нашу программу для игры в "Камень, Ножницы, Бумага", работающую посредством захвата жестов с веб-камеры.

🚀 #**О проекте**

Это десктоп-приложение, которое позволяет играть в классическую игру "Камень, Ножницы, Бумага" с использованием веб-камеры. Приложение распознаёт жест руки пользователя с помощью компьютерного зрения и определяет победителя в реальном времени.

🛠️ #**Технологии**

**OpenCV:** Для обработки изображений с веб-камеры.

**MediaPipe:** Для распознавания жестов руки.

**Tkinter:** Для создания графического интерфейса.

Попытка использовать предложенный кураторами сервис не увенчалась успехом: модель не удовлетворяла требованиям точности и возникали ошибки с развертыванием. Тогда наша команда приняла решение использовать другую технологию: MediaPipe от Google, чтобы отслеживать положение пальцев пользователя и определять жест. 
Такое решение оказалось не только менее чувствительным к зависимостям и версии Python, но и намного более точным.

📦 #**Установка**

Убедитесь, что ваша версия Python 3.9 - 3.12:
 
    python --version
    
Клонируйте репозиторий:

    git clone https://github.com/ваш-username/ваш-репозиторий.git

Установите зависимости:

    pip install -r requirements.txt

Запустите приложение:

    python main.py

🎮 #**Как играть**

Запустите приложение. Нажмите кнопку "Начать бой" и покажите свой жест в веб-камеру до истечения таймера. После появления результатов можете начать бой снова.

Жесты:

✊ Камень

✌️ Ножницы

🤚 Бумага

Правила:
    • Камень бьет ножницы
    • Ножницы режут бумагу
    • Бумага покрывает камень

👥 #**Команда**

Эдуард Жданов - разработка и отладка модели

Артем Бабичев - создание интерфейса

Игорь Лаптев - рефакторинг кода и отладка багов
