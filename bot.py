import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
from database import create_db
from bot_functions import register, new_order, view_orders


main_menu_keyboard = [
    ['Арендовать бокс', 'Правила хранения'],
    ['Адреса складов', 'Связаться с нами']
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=main_menu_markup
    )


def handle_main_menu(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Арендовать бокс':
        inline_keyboard = [
            [InlineKeyboardButton("Оформить аренду", callback_data='rent_form')],
            [InlineKeyboardButton("Бесплатный вывоз", callback_data='free_pickup')],
            [InlineKeyboardButton("Список вещей", callback_data='item_list')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif update.message.text == 'Правила хранения':
        inline_keyboard = [
            [InlineKeyboardButton("Разрешённые вещи", callback_data='allowed_items')],
            [InlineKeyboardButton("Запрещённые вещи", callback_data='prohibited_items')],
            [InlineKeyboardButton("Условия хранения", callback_data='storage_conditions')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif update.message.text == 'Адреса складов':
        inline_keyboard = [
            [InlineKeyboardButton("Показать на карте", callback_data='show_on_map')],
            [InlineKeyboardButton("Список адресов", callback_data='address_list')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    elif update.message.text == 'Связаться с нами':
        inline_keyboard = [
            [InlineKeyboardButton("Электронная почта", callback_data='email')],
            [InlineKeyboardButton("Телефон", callback_data='phone')],
            [InlineKeyboardButton("Сообщение в телеграм", callback_data='telegram_message')]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'rent_form':
        query.edit_message_text(text="Форма для оформления аренды.")
    elif query.data == 'free_pickup':
        query.edit_message_text(text="Информация о бесплатном вывозе.")
    elif query.data == 'item_list':
        query.edit_message_text(text="Список вещей.")
    elif query.data == 'allowed_items':
        query.edit_message_text(text="Разрешённые вещи.")
    elif query.data == 'prohibited_items':
        query.edit_message_text(text="Запрещённые вещи.")
    elif query.data == 'storage_conditions':
        query.edit_message_text(text="Условия хранения.")
    elif query.data == 'show_on_map':
        query.edit_message_text(text="Показать на карте.")
    elif query.data == 'address_list':
        query.edit_message_text(text="Список адресов.")
    elif query.data == 'email':
        query.edit_message_text(text="Электронная почта.")
    elif query.data == 'phone':
        query.edit_message_text(text="Телефон.")
    elif query.data == 'telegram_message':
        query.edit_message_text(text="Сообщение в телеграм.")


if __name__ == '__main__':
    load_dotenv()
    TOKEN_TG = os.getenv('TOKEN_TG')
    create_db()
    updater = Updater(TOKEN_TG, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("neworder", new_order))
    dispatcher.add_handler(CommandHandler("vieworders", view_orders))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_main_menu))

    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()
