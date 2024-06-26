import sqlite3


def create_db():
    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY,
                 username TEXT,
                 phone TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                 order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 item_description TEXT,
                 start_date TEXT,
                 end_date TEXT,
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()
