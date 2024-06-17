import sqlite3
from datetime import datetime
from telebot import TeleBot, types
from config import token, ADMIN_ID


bot = TeleBot(token)

# Функция для определения типа недели
def get_week_type():
    week_number = datetime.now().isocalendar()[1]
    return 'числитель' if week_number % 2 != 0 else 'знаменатель'

# Функция для получения группы пользователя из базы данных
def get_user_group(user_id):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('SELECT group_name FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Функция для установки группы пользователя в базе данных
def set_user_group(user_id, group_name):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, group_name) VALUES (?, ?)', (user_id, group_name))
    conn.commit()
    conn.close()

# Функция для получения расписания из базы данных
def get_schedule(group_name, week_type, day):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('SELECT schedule FROM schedule WHERE group_name = ? AND week_type = ? AND day = ?', (group_name, week_type, day))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "Расписание не найдено."

# Функция для установки роли пользователя
def set_user_role(user_id, role):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE user_id = ?', (role, user_id))
    conn.commit()
    conn.close()

# Функция для получения роли пользователя
def get_user_role(user_id):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'student'

# Функция для добавления контента (новости или мероприятия)
def add_content(content_type, content):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    if content_type == 'news':
        c.execute('INSERT INTO news (content) VALUES (?)', (content,))
    elif content_type == 'events':
        c.execute('INSERT INTO events (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()

# Функция для получения контента (новости или мероприятия)
def get_content(content_type):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    if content_type == 'news':
        c.execute('SELECT content, timestamp FROM news ORDER BY timestamp DESC')
    elif content_type == 'events':
        c.execute('SELECT content, timestamp FROM events ORDER BY timestamp DESC')
    results = c.fetchall()
    conn.close()
    return results

# Функция для перевода дней недели на русский
def translate_day_to_russian(day):
    days = {
        'Monday': 'понедельник',
        'Tuesday': 'вторник',
        'Wednesday': 'среда',
        'Thursday': 'четверг',
        'Friday': 'пятница',
        'Saturday': 'суббота',
        'Sunday': 'воскресенье'
    }
    return days.get(day, day)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    role = get_user_role(user_id)
    if not role:
        set_user_role(user_id, 'student')
        role = 'student'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)     
    groups = ["1-ТИД-5", "1-ТИД-6", "2-ТИД-5", "2-ТИД-6",
             "3-ТИД-5", "3-ТИД-6", "4-ТИД-5", "4-ТИД-6", "1-МГ-18", "2-МГ-18"]
    for group in groups:
        markup.add(types.KeyboardButton(group))
    bot.send_message(user_id, "Привет! Выбери свою группу:", reply_markup=markup)

# Обработчик выбора группы
@bot.message_handler(func=lambda message: message.text in ["1-ТИД-5", "1-ТИД-6", "2-ТИД-5", "2-ТИД-6",
                                             "3-ТИД-5", "3-ТИД-6", "4-ТИД-5", "4-ТИД-6", "1-МГ-18", "2-МГ-18"])
def select_group(message):
    group = message.text
    set_user_group(message.chat.id, group)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    schedule_button = types.KeyboardButton("Расписание на сегодня")
    news_button = types.KeyboardButton("Новости")
    events_button = types.KeyboardButton("Мероприятия")
    feedback_button = types.KeyboardButton("Обратная связь")
    help_button = types.KeyboardButton("Помощь")
    markup.add(schedule_button, news_button, events_button, feedback_button, help_button)
    bot.send_message(message.chat.id, f"Нажмите на кнопку, чтобы получить расписание, новости или мероприятия. Чтобы выбрать другую группу, введите команду /start.", reply_markup=markup)

# Обработчик запроса расписания
@bot.message_handler(func=lambda message: message.text == "Расписание на сегодня")
def send_schedule(message):
    user_group = get_user_group(message.chat.id)
    if not user_group:
        bot.send_message(message.chat.id, "Сначала выберите свою группу с помощью команды /start.")
        return
    current_day = datetime.now().strftime('%A')
    week_type = get_week_type()
    today_schedule = get_schedule(user_group, week_type, current_day)
    day_in_russian = translate_day_to_russian(current_day)
    response = f"Сегодня {day_in_russian}. Тип недели: {week_type}.\n{today_schedule}"
    bot.send_message(message.chat.id, response)

# Обработчик запроса новостей
@bot.message_handler(func=lambda message: message.text == "Новости")
def send_news(message):
    news_list = get_content('news')
    if not news_list:
        bot.send_message(message.chat.id, "Нет новостей на данный момент.")
        return
    response = "Последние новости:\n\n"
    for news in news_list:
        response += f"{news[1]}: {news[0]}\n\n"
    bot.send_message(message.chat.id, response)

# Обработчик запроса мероприятий
@bot.message_handler(func=lambda message: message.text == "Мероприятия")
def send_events(message):
    events_list = get_content('events')
    if not events_list:
        bot.send_message(message.chat.id, "Нет мероприятий на данный момент.")
        return
    response = "Последние мероприятия:\n\n"
    for event in events_list:
        response += f"{event[1]}: {event[0]}\n\n"
    bot.send_message(message.chat.id, response)

# Обработчик добавления новостей
@bot.message_handler(func=lambda message: message.text == "Добавить новость" and get_user_role(message.chat.id) == 'methodist')
def add_news_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    msg = bot.send_message(message.chat.id, "Введите текст новости или нажмите 'Назад' чтобы вернуться:", reply_markup=markup)
    bot.register_next_step_handler(msg, save_news)

def save_news(message):
    if message.text == "Назад":
        select_group(message)
    else:
        add_content('news', message.text)
        bot.send_message(message.chat.id, "Новость успешно добавлена.")
        select_group(message)

# Обработчик добавления мероприятий
@bot.message_handler(func=lambda message: message.text == "Добавить мероприятие" and get_user_role(message.chat.id) == 'methodist')
def add_events_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    msg = bot.send_message(message.chat.id, "Введите информацию для публикации или нажмите 'Назад' чтобы вернуться:", reply_markup=markup)
    bot.register_next_step_handler(msg, save_event)

def save_event(message):
    if message.text == "Назад":
        select_group(message)
    else:
        add_content('events', message.text)
        bot.send_message(message.chat.id, "Мероприятие успешно добавлено.")
        select_group(message)

# Обработчик команды для назначения роли методиста
@bot.message_handler(commands=['set_methodist'])
def set_methodist(message):
    if message.chat.id == ADMIN_ID:  # Проверка, что команду выполняет администратор
        msg = bot.send_message(message.chat.id, "Введите ID пользователя, которому нужно назначить роль методиста:")
        bot.register_next_step_handler(msg, save_methodist)

def save_methodist(message):
    try:
        user_id = int(message.text)
        set_user_role(user_id, 'methodist')
        bot.send_message(message.chat.id, f"Пользователь с ID {user_id} теперь методист.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат ID. Пожалуйста, введите числовой ID.")

# Обработчик обратной связи от студентов к методисту
@bot.message_handler(func=lambda message: message.text == "Обратная связь")
def feedback_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    msg = bot.send_message(message.chat.id, "Введите ваше сообщение для методиста или нажмите 'Назад' чтобы вернуться:", reply_markup=markup)
    bot.register_next_step_handler(msg, send_feedback_to_methodist)

def send_feedback_to_methodist(message):
    if message.text == "Назад":
        select_group(message)
    else:
        user_username = message.from_user.username
        #user_id = message.chat.id
        user_message = message.text
        methodist_id = get_methodist_id()  
        bot.send_message(methodist_id, f"Новое сообщение от студента @{user_username}:\n{user_message}")
        bot.send_message(message.chat.id, "Ваше сообщение было отправлено методисту.")
        select_group(message)

def get_methodist_id():
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE role = 'methodist'")
    result = c.fetchone()
    conn.close()
    return result[0] if result else ADMIN_ID

# Обработчик команды "Помощь"
@bot.message_handler(func=lambda message: message.text == "Помощь")
def send_help(message):
    help_text = (
        "Список доступных команд:\n"
        "- Расписание на сегодня: расписание на текущий день.\n"
        "- Новости: просмотреть последние новости.\n"
        "- Мероприятия: просмотреть предстоящие мероприятия.\n"
        "- Обратная связь: отправить сообщение методисту.\n"
        "\n"
        "Чтобы выбрать другую группу, введите команду /start."
    )
    bot.send_message(message.chat.id, help_text)

bot.polling()
