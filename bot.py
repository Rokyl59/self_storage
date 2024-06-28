import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
from database import create_db, add_user, get_user, create_order, get_orders, \
    update_order_status, get_user_orders, set_admin, check_admin, get_all_users
from bot_functions import allowed_items, prohibited_items, storage_conditions
from datetime import datetime, timedelta
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not get_user(user.id):
        add_user(user.id, user.username, None)
    if get_user(user.id)[3]:
        update.message.reply_text(
            fr'Привет, {user.mention_markdown_v2()}\!',
            reply_markup=admin_menu_markup
        )
    else:
        update.message.reply_text(
            fr'Привет, {user.mention_markdown_v2()}\!',
            reply_markup=main_menu_markup
        )


def handle_main_menu(update: Update, context: CallbackContext) -> None:
    if update.message.text == '🗄️ Арендовать бокс':
        inline_keyboard = [
            [InlineKeyboardButton("Оформить аренду",
                                  callback_data='rent_form')],
            [InlineKeyboardButton("Бесплатный вывоз",
                                  callback_data='free_pickup')],
            [InlineKeyboardButton("Список вещей",
                                  callback_data='item_list')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif update.message.text == '📜 Правила хранения':
        inline_keyboard = [
            [InlineKeyboardButton("Разрешённые вещи",
                                  callback_data='allowed_items')],
            [InlineKeyboardButton("Запрещённые вещи",
                                  callback_data='prohibited_items')],
            [InlineKeyboardButton("Условия хранения",
                                  callback_data='storage_conditions')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text(
            'Для удобства и безопасности наших клиентов и \
             сотрудников, мы разработали правила хранения вещей. \
             Пожалуйста, ознакомьтесь с ними перед тем, как \
             арендовать склад.', reply_markup=reply_markup)
    elif update.message.text == '📍 Адреса складов':
        inline_keyboard = [
            [InlineKeyboardButton("Показать на карте",
                                  callback_data='show_on_map')],
            [InlineKeyboardButton("Список адресов",
                                  callback_data='address_list')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif update.message.text == '📞 Связаться с нами':
        inline_keyboard = [
            [InlineKeyboardButton("Электронная почта", callback_data='email')],
            [InlineKeyboardButton("Телефон", callback_data='phone')],
            [InlineKeyboardButton("Сообщение в телеграм",
                                  callback_data='telegram_message')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif (update.message.text == '🔧 Админка' and
          check_admin(update.effective_user.id)):
        inline_keyboard = [
            [InlineKeyboardButton("Посмотреть пользователей",
                                  callback_data='admin_show_user')],
            [InlineKeyboardButton("Посмотреть просроченные заказы",
                                  callback_data='admin_show_ticket')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'rent_form':
        query.edit_message_text(text=(
            "Введите описание вещей, которые вы хотите хранить, "
            "и срок аренды (например, 'Снегоход, лыжи - 3 месяца'")
        )
        context.user_data['expected_message'] = 'rent_form'
    elif query.data == 'free_pickup':
        query.edit_message_text(text=(
            "Информация о бесплатном вывозе. "
            "Укажите адрес и контактный номер телефона.")
        )
        context.user_data['expected_message'] = 'free_pickup'
    elif query.data == 'item_list':
        user_id = query.from_user.id
        orders = get_user_orders(user_id)
        if orders:
            orders_text = "\n".join([
                f"Заказ {order[0]}: {order[2]}, срок аренды до {order[4]}"
                for order in orders])
        else:
            orders_text = "У вас нет активных заказов."
        query.edit_message_text(text=f"Ваши заказы:\n{orders_text}")
    elif query.data == 'allowed_items':
        query.edit_message_text(text=allowed_items(), parse_mode='Markdown')
    elif query.data == 'prohibited_items':
        query.edit_message_text(text=prohibited_items(), parse_mode='Markdown')
    elif query.data == 'storage_conditions':
        query.edit_message_text(
            text=storage_conditions(), parse_mode='Markdown')
    elif query.data == 'show_on_map':
        query.edit_message_text(text="Показать на карте: адреса складов.")
    elif query.data == 'address_list':
        query.edit_message_text(
            text="Список адресов: ул. Примерная, д. 1 и др.")
    elif query.data == 'email':
        query.edit_message_text(text="Электронная почта: example@example.com")
    elif query.data == 'phone':
        query.edit_message_text(text="Телефон: +7 123 456 78 90")
    elif query.data == 'telegram_message':
        query.edit_message_text(text="Сообщение в телеграм: @example")
    elif query.data == 'admin_show_user':
        query.edit_message_text(text=f"{get_users()}")


def handle_text_messages(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if 'expected_message' in context.user_data:
        if context.user_data['expected_message'] == 'rent_form':
            item_description, duration = update.message.text.split(' - ')
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (
                datetime.now() + timedelta(days=int(duration.split()[0]) * 30)
                ).strftime('%Y-%m-%d')
            create_order(user.id, item_description, start_date, end_date)
            update.message.reply_text(
                'Ваш заказ был успешно создан!',
                reply_markup=main_menu_markup
            )
            context.user_data.pop('expected_message')
        elif context.user_data['expected_message'] == 'free_pickup':
            update.message.reply_text(
                'Скоро с вами свяжется наш менеджер',
                reply_markup=main_menu_markup
            )
            context.user_data.pop('expected_message')
    else:
        handle_main_menu(update, context)


def send_reminders(context: CallbackContext):
    orders = get_orders()
    for order in orders:
        user_id = order[1]
        end_date = datetime.strptime(order[4], '%Y-%m-%d')
        now = datetime.now()
        if now > end_date - timedelta(days=30) and now <= end_date - timedelta(days=29):
            context.bot.send_message(
                chat_id=user_id,
                text="Напоминание: Ваша аренда заканчивается через месяц.")
        elif now > end_date - timedelta(days=14) and now <= end_date - timedelta(days=13):
            context.bot.send_message(
                chat_id=user_id,
                text="Напоминание: Ваша аренда заканчивается через две недели.")
        elif now > end_date - timedelta(days=7) and now <= end_date - timedelta(days=6):
            context.bot.send_message(
                chat_id=user_id,
                text="Напоминание: Ваша аренда заканчивается через неделю.")
        elif now > end_date - timedelta(days=3) and now <= end_date - timedelta(days=2):
            context.bot.send_message(
                chat_id=user_id,
                text="Напоминание: Ваша аренда заканчивается через три дня.")
        elif now > end_date:
            context.bot.send_message(
                chat_id=user_id,
                text="Ваша аренда закончилась. Вещи будут храниться по повышенному тарифу в течение 6 месяцев.")
            update_order_status(order[0], 'expired')


def admin_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not get_user(user.id):
        update.message.reply_text("Вы не зарегистрированы в системе.")
        return

    credentials = context.args[0] if context.args else ""
    if credentials == ADMIN_CREDENTIALS:
        set_admin(user.id)
        update.message.reply_text("Вы успешно стали администратором!",
                                  reply_markup=admin_menu_markup)
    else:
        update.message.reply_text("Неверные данные для входа.")


def get_users():
    users = get_all_users()

    if not users:
        return "На данный момент в системе нет пользователей."

    users_text = "\n\n".join([
        f"ID: {user[0]}\nUsername: {user[1]}\nАдминистратор: {'Да' if user[2] else 'Нет'}"
        for user in users
    ])

    return f"Список зарегистрированных пользователей:\n\n{users_text}"


if __name__ == '__main__':
    main_menu_keyboard = [
        ['🗄️ Арендовать бокс', '📜 Правила хранения'],
        ['📍 Адреса складов', '📞 Связаться с нами']
    ]

    admin_menu_keyboard = [
        ['🗄️ Арендовать бокс', '📜 Правила хранения'],
        ['📍 Адреса складов', '📞 Связаться с нами'],
        ['🔧 Админка']
    ]

    main_menu_markup = ReplyKeyboardMarkup(
        main_menu_keyboard,
        resize_keyboard=True)
    admin_menu_markup = ReplyKeyboardMarkup(
        admin_menu_keyboard,
        resize_keyboard=True)

    load_dotenv()
    create_db()
    TOKEN_TG = os.getenv('TOKEN_TG')
    ADMIN_CREDENTIALS = os.getenv('ADMIN_CREDENTIALS')
    updater = Updater(TOKEN_TG, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("admin", admin_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                          handle_text_messages))
    dispatcher.add_handler(CallbackQueryHandler(button))

    job_queue = updater.job_queue
    job_queue.run_repeating(send_reminders, interval=86400, first=0)

    updater.start_polling()
    updater.idle()
