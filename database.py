import sqlite3


def create_db():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY,
                 username TEXT,
                 phone TEXT,
                 is_admin BOOLEAN DEFAULT FALSE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 item_description TEXT,
                 start_date TIMESTAMP,
                 end_date TIMESTAMP,
                 status TEXT,
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    c.execute('''CREATE TABLE IF NOT EXIST clicked_users (
                 click_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 telegram_id INTEGER,
                 click_date TIMESTAMP
                 )
              ''')
    conn.commit()
    conn.close()


def add_user(user_id, username, phone):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        ('INSERT INTO users (user_id, '
         'username, phone) '
         'VALUES (?, ?, ?)'),
        (user_id, username, phone))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def create_order(user_id, item_description, start_date, end_date):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        ('INSERT INTO orders (user_id, item_description, '
         'start_date, end_date, status) '
         'VALUES (?, ?, ?, ?, ?)'),
        (user_id, item_description, start_date, end_date, 'active'))
    conn.commit()
    conn.close()


def get_orders():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders')
    orders = c.fetchall()
    conn.close()
    return orders


def update_order_status(order_id, status):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        ('UPDATE orders SET status = ? '
         'WHERE order_id = ?'),
        (status, order_id))
    conn.commit()
    conn.close()


def get_user_orders(user_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,))
    orders = c.fetchall()
    conn.close()
    return orders


def set_admin(user_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_admin = TRUE WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def update_clicked_users(telegram_id, click_date):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO clicked_users (telegram_id, click_date) VALUES (?, ?)',
        (telegram_id, click_date)
    )
    conn.commit()
    conn.close()


def get_clicked_users():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    all_count = c.execute('SELECT COUNT(click_id) FROM clicked_users').fetchone()[0]
    unique_count = c.execute('SELECT COUNT(DISTINCT telegram_id) FROM clicked_users').fetchone()[0]
    conn.close()
    return f'Общее количество кликнувших {all_count}, количество уникальных пользователей{unique_count}'
