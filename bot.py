import os
import logging


from dotenv import load_dotenv
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, CallbackContext


from database import create_db, add_user, get_user, create_order, get_orders, \
    update_order_status, get_user_orders, set_admin, check_admin, \
    get_all_users, get_addresses, get_order_details
from bot_functions import allowed_items, prohibited_items, storage_conditions


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
            fr'Привет, `{user.username}`!',
            reply_markup=admin_menu_markup,
            parse_mode='Markdown'
        )
    else:
        update.message.reply_text(
            fr'Привет, `{user.username}`!',
            reply_markup=main_menu_markup,
            parse_mode='Markdown'
        )


def handle_main_menu(update: Update, context: CallbackContext) -> None:

    if update.message.text == '🗄️ Арендовать бокс':
        addresses = get_addresses()
        inline_keyboard = [[InlineKeyboardButton(
            address[1],
            callback_data=f'address_{address[0]}')] for address in addresses]
        inline_keyboard.append([InlineKeyboardButton(
            "Бесплатный вывоз", callback_data='free_pickup')])
        inline_keyboard.append([InlineKeyboardButton(
            "Мои заказы", callback_data='my_orders')])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text(
            'Для аренды бокса выберите один из адресов ниже. '
            'Или вы можете сделать бесплатный вызов, указав свой адрес, '
            'но перед заказом прочитайте `Правила Хранения`\n\n'
            'Примечание: `Габариты будет измерять доставщик.`',
            reply_markup=reply_markup,
            parse_mode='Markdown')

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
        addresses = get_addresses()
        addresses_text = "\n".join([f"{index + 1}. {address[1]}"
                                    for index, address in enumerate(addresses)])
        update.message.reply_text(f"Список адресов складов:\n{addresses_text}")

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

    if query.data.startswith('address_'):
        address_id = query.data.split('_')[1]
        addresses = get_addresses()
        address = next((addr[1] for addr in addresses
                        if addr[0] == int(address_id)), "Неизвестный адрес")
        query.edit_message_text(
            text=f"Вы выбрали адрес склада: {address}. "
                 "Введите описание вещей, которые вы хотите хранить, "
                 "и срок аренды (например, 'Снегоход, лыжи - 3 месяца')."
        )
        context.user_data['expected_message'] = 'rent_form'
        context.user_data['address'] = address

    elif query.data == 'free_pickup':
        query.edit_message_text(
            text=("Предполагаемая цена - 1000 рублей в месяц "
                  "Пожалуйста, введите ваш адрес и контактный номер телефона. "
                  "Доставщик свяжется с вами для подтверждения. "
                  "Пример: '`ул. Тургенева, д. 10, тел. +79876543210`'"),
            parse_mode='Markdown'
        )
        context.user_data['expected_message'] = 'free_pickup'

    elif query.data == 'my_orders':
        user_id = query.from_user.id
        orders = get_user_orders(user_id)
        if orders:
            orders_text = "\n".join([
                f"`Заказ {order[0]}:` {order[2]}, срок аренды до `{order[4]}` на складе: `{order[6]}`\n"
                for order in orders])
            order_buttons = [
                [InlineKeyboardButton(f"Заказ {order[0]}", callback_data=f'order_{order[0]}')] for order in orders
            ]
            order_buttons.append([InlineKeyboardButton("Забрать все", callback_data='take_all')])
            inline_keyboard = InlineKeyboardMarkup(order_buttons)
            query.edit_message_text(
                text=f"Ваши заказы:\n{orders_text}",
                reply_markup=inline_keyboard,
                parse_mode='Markdown'
            )
        else:
            query.edit_message_text(
                text="У вас нет активных заказов."
            )

    elif query.data.startswith('order_'):
        order_id = int(query.data.split('_')[1])
        order_details = get_order_details(order_id)
        query.edit_message_text(
            text=f"Заказ `{order_id}`: {order_details[2]}, срок аренды до `{order_details[4]}` на складе: `{order_details[6]}`\nВыберите действие:",
            reply_markup=delivery_options_markup(),
            parse_mode='Markdown'
        )

    elif query.data == 'take_all':
        query.edit_message_text(
            text="Выберите вариант выполнения заказа:",
            reply_markup=take_all_options_markup()
        )

    elif query.data == 'pickup_all':
        query.edit_message_text(
            text="Вы выбрали самовывоз. Заберите заказы"
        )

    elif query.data == 'delivery_home_all':
        order_id = query.data.split('_')[1]
        context.user_data['order_id'] = order_id
        query.edit_message_text(
            text="Пожалуйста, укажите адрес и контактный номер телефона для доставки на дом всех заказов. \nПример: '`ул. Тургенева, д. 10, тел. +79876543210`'",
            parse_mode='Markdown'
        )
        context.user_data['expected_message'] = 'delivery_home_all'

    elif query.data.startswith('delivery_home'):
        order_id = query.data.split('_')[1]
        context.user_data['order_id'] = order_id
        query.edit_message_text(
            text="Пожалуйста, укажите адрес и контактный номер телефона для доставки на дом. \nПример: '`ул. Тургенева, д. 10, тел. +79876543210`'",
            parse_mode='Markdown'
        )
        context.user_data['expected_message'] = 'delivery_home'

    elif query.data == 'pickup':
        query.edit_message_text(
            text="Вы выбрали самовывоз. Заберите заказ"
        )

    elif query.data == 'allowed_items':
        query.edit_message_text(text=allowed_items(), parse_mode='Markdown')

    elif query.data == 'prohibited_items':
        query.edit_message_text(text=prohibited_items(), parse_mode='Markdown')

    elif query.data == 'storage_conditions':
        query.edit_message_text(
            text=storage_conditions(), parse_mode='Markdown')

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
            address = context.user_data.get('address', 'Неизвестный адрес')
            create_order(
                user.id, item_description, start_date, end_date, address)
            update.message.reply_text(
                'Ваш заказ был успешно создан!',
                reply_markup=main_menu_markup
            )
            context.user_data.pop('expected_message')
            context.user_data.pop('address')

        elif context.user_data['expected_message'] == 'free_pickup':
            update.message.reply_text(
                'Скоро с вами свяжется наш доставщик',
                reply_markup=main_menu_markup
            )
            context.user_data.pop('expected_message')

        elif context.user_data.get('expected_message') == 'delivery_home':
            order_id = context.user_data.get('order_id')
            if order_id:
                update.message.reply_text(
                    'Спасибо! Ваш заказ на доставку на дом будет обработан.',
                    reply_markup=main_menu_markup
                )
                context.user_data.pop('expected_message')
                context.user_data.pop('order_id')

            else:
                update.message.reply_text(
                    'Что-то пошло не так. Пожалуйста, попробуйте ещё раз.'
                )

        elif context.user_data.get('expected_message') == 'delivery_home_all':
            order_id = context.user_data.get('order_id')
            if order_id:
                update.message.reply_text(
                    'Спасибо! Ваши заказы на доставку на дом будет обработаны.',
                    reply_markup=main_menu_markup
                )
                context.user_data.pop('expected_message')
                context.user_data.pop('order_id')
            else:
                update.message.reply_text(
                    'Что-то пошло не так. Пожалуйста, попробуйте ещё раз.'
                )
    else:
        handle_main_menu(update, context)


def delivery_options_markup():
    inline_keyboard = [
        [InlineKeyboardButton("Доставка на дом", callback_data='delivery_home')],
        [InlineKeyboardButton("Самовывоз", callback_data='pickup')]
    ]
    return InlineKeyboardMarkup(inline_keyboard)


def take_all_options_markup():
    inline_keyboard = [
        [InlineKeyboardButton(
            "Доставка на дом",
            callback_data='delivery_home_all')],
        [InlineKeyboardButton("Самовывоз", callback_data='pickup_all')]
    ]
    return InlineKeyboardMarkup(inline_keyboard)


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
