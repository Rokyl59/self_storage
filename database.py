import sqlite3


def create_db():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 username TEXT,
                 phone TEXT,
                 email TEXT,
                 is_admin BOOLEAN DEFAULT FALSE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 item_description TEXT,
                 start_date DATETIME,
                 end_date DATETIME,
                 status TEXT,
                 address TEXT,
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS clicked_users (
                 click_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 telegram_id INTEGER,
                 click_date TIMESTAMP
                 )
              ''')
    c.execute('''CREATE TABLE IF NOT EXISTS addresses (
                 address_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 address TEXT)''')
    conn.commit()
    conn.close()


def add_user(user_id, username, phone, email):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        ('INSERT INTO users (user_id, '
         'username, phone, email) '
         'VALUES (?, ?, ?, ?)'),
        (user_id, username, phone, email))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def create_order(user_id, item_description, start_date, end_date, address):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute(
        ('INSERT INTO orders (user_id, item_description, '
         'start_date, end_date, status, address) '
         'VALUES (?, ?, ?, ?, ?, ?)'),
        (user_id, item_description, start_date, end_date, 'active', address))
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


def check_admin(user_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id, ))
    is_admin = c.fetchone()[0]
    conn.close()
    return is_admin


def get_all_users():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, is_admin FROM users')
    users = c.fetchall()
    conn.close()
    return users


def get_addresses():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM addresses')
    addresses = c.fetchall()
    conn.close()
    return addresses


def get_order_details(order_id):
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    order = c.fetchone()
    conn.close()
    return order
