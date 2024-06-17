import sqlite3

# Создаем базу данных
conn = sqlite3.connect('schedule.db')
c = conn.cursor()

# Таблица для хранения пользователей
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    group_name TEXT,
    role TEXT
)
''')

# Таблица для хранения расписания
c.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT,
    week_type TEXT,
    day TEXT,
    schedule TEXT
)
''')

# Таблица для хранения новостей
c.execute('''
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Таблица для хранения мероприятий
c.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

def add_schedule(group_name, week_type, day, schedule):
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute('INSERT INTO schedule (group_name, week_type, day, schedule) VALUES (?, ?, ?, ?)', 
              (group_name, week_type, day, schedule))
    conn.commit()
    conn.close()
    print(f"Расписание для {group_name}, {week_type}, {day} успешно добавлено.")

'''
# Пример использования
add_schedule('group1', 'числитель', 'Monday', '09:00 - Math\n11:00 - Physics\n13:00 - Literature')
add_schedule('group1', 'знаменатель', 'Wednesday', '09:00 - Chemistry\n11:00 - Biology\n13:00 - History')
add_schedule('group2', 'числитель', 'Monday', '09:00 - English\n11:00 - Geography\n13:00 - Computer Science')
add_schedule('group2', 'знаменатель', 'Monday', '09:00 - Music\n11:00 - Art\n13:00 - PE')
'''

print("Расписание успешно добавлено в базу данных.")


conn.commit()
conn.close()

print("База данных успешно создана и инициализирована.")
