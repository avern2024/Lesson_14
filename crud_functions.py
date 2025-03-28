import sqlite3


def initiate_db(db_name="products.db"):
    """Создаёт таблицы Products и Users, если они ещё не созданы."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Создание таблицы Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')

    # Создание таблицы Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    ''')

    connection.commit()
    connection.close()


def get_all_products(db_name="products.db"):
    """Возвращает все записи из таблицы Products."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    connection.close()
    return products


def populate_db(db_name="products.db"):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    products = [
        ("Клубника", "41 ккал", 500),
        ("Томаты", "20 ккал", 200),
        ("Мандарины", "38 ккал", 252),
        ("Яблоки", "47 ккал", 174),
        ("Молоко", "64 ккал", 100),
        ("Бананы", "89 ккал", 140),
        ("Морковь", "41 ккал", 39),
        ("Картофель", "76 ккал", 50),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO Products (title, description, price) VALUES (?, ?, ?)",
        products
    )

    connection.commit()
    connection.close()


def create_images_table(db_name="products.db"):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductImages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES Products (id) ON DELETE CASCADE
    )
    ''')

    connection.commit()
    connection.close()


def populate_images_table(db_name="products.db"):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    images = [
        (1, "kl.jpg"),
        (2, "tomato.jpg"),
        (3, "mandarin.jpg"),
        (4, "apple.jpg"),
        (5, "milk.jpg"),
        (6, "bananas.jpg"),
        (7, "carrots.jpg"),
        (8, "potato.jpg"),
    ]

    cursor.executemany("INSERT INTO ProductImages (product_id, image_path) VALUES (?, ?)", images)
    connection.commit()
    connection.close()


def remove_duplicates(db_name="products.db"):
    """Удаление дубликатов из таблицы"""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    print("Удаление дубликатов из таблицы Products...")
    cursor.execute('''
    DELETE FROM Products
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM Products
        GROUP BY title, description, price
    )
    ''')
    print("Дубликаты удалены из таблицы Products.")

    print("Удаление дубликатов из таблицы ProductImages...")
    cursor.execute('''
    DELETE FROM ProductImages
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM ProductImages
        GROUP BY product_id, image_path
    )
    ''')

    connection.commit()
    connection.close()
    print("Дубликаты удалены из таблиц Products и ProductImages.")


def add_user(username, email, age, db_name="products.db"):
    """Добавляет нового пользователя в таблицу Users."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
    INSERT INTO Users (username, email, age, balance) 
    VALUES (?, ?, ?, ?)
    ''', (username, email, age, 1000))

    connection.commit()
    connection.close()


def is_included(username, db_name="products.db"):
    """Проверяет, существует ли пользователь с данным именем."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute('''
    SELECT 1 FROM Users WHERE username = ? LIMIT 1
    ''', (username,))
    result = cursor.fetchone()

    connection.close()
    return result is not None


if __name__ == "__main__":
    initiate_db()
    populate_db()
    create_images_table()
    populate_images_table()
    remove_duplicates()


