import sqlite3
from telegram import Update
from telegram.ext import CallbackContext


def register(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    phone = context.args[0] if context.args else None

    if phone:
        conn = sqlite3.connect('storage.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (user_id, username, phone) VALUES (?, ?, ?)', (user_id, username, phone))
        conn.commit()
        conn.close()
        update.message.reply_text(f'Регистрация прошла успешно! Ваш телефон: {phone}')
    else:
        update.message.reply_text('Пожалуйста, укажите ваш номер телефона после команды /register.')


def new_order(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    item_description = ' '.join(context.args) if context.args else 'Описание отсутствует'
    start_date = '2024-06-26'
    end_date = '2024-12-26'

    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('INSERT INTO orders (user_id, item_description, start_date, end_date) VALUES (?, ?, ?, ?)', (user_id, item_description, start_date, end_date))
    conn.commit()
    conn.close()

    update.message.reply_text(f'Ваш заказ принят! Описание: {item_description}')


def view_orders(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    conn = sqlite3.connect('storage.db')
    c = conn.cursor()
    c.execute('SELECT order_id, item_description, start_date, end_date FROM orders WHERE user_id = ?', (user_id,))
    orders = c.fetchall()
    conn.close()

    if orders:
        response = 'Ваши заказы:\n'
        for order in orders:
            response += f'Заказ {order[0]}: {order[1]}, с {order[2]} по {order[3]}\n'
    else:
        response = 'У вас нет активных заказов.'

    update.message.reply_text(response)
