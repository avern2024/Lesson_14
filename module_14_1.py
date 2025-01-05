import sqlite3

# Создание и подключение к базе данных
conn = sqlite3.connect('not_telegram.db')
cursor = conn.cursor()

# Создание таблицы Users
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER,
        balance INTEGER NOT NULL
    )
''')

# Заполнение таблицы 10 записями
users = [
    (f'User{i}', f'example{i}@gmail.com', i * 10, 1000)
    for i in range(1, 11)
]

cursor.executemany('''
    INSERT INTO Users (username, email, age, balance)
    VALUES (?, ?, ?, ?)
''', users)

# Обновление balance у каждой 2ой записи, начиная с 1ой на 500
cursor.execute('''
    UPDATE Users
    SET balance = 500
    WHERE id % 2 = 1
''')

# Удаление каждой 3ей записи, начиная с 1ой
cursor.execute("SELECT id FROM Users")
rows = cursor.fetchall()

for index, row in enumerate(rows, start=1):
    if index % 3 == 1:  # Каждая третья запись по порядку (начиная с 1-й)
        cursor.execute("DELETE FROM Users WHERE id = ?", (row[0],))

# Выборка всех записей, где возраст не равен 60
cursor.execute('''
    SELECT username, email, age, balance
    FROM Users
    WHERE age != 60
''')
results = cursor.fetchall()

# Вывод результатов в консоль
for row in results:
    print(f"Имя: {row[0]} | Почта: {row[1]} | Возраст: {row[2]} | Баланс: {row[3]}")

# Фиксация изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()
