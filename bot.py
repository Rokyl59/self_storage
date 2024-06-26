import os
from telegram import Update
from dotenv import load_dotenv
from database import create_db
from bot_functions import register, new_order, view_orders
from telegram.ext import Updater, CommandHandler, CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Используйте /start для начала работы.')


if __name__ == '__main__':
    load_dotenv()
    TOKEN_TG = os.getenv('TOKEN_TG')
    create_db()
    updater = Updater(TOKEN_TG, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("neworder", new_order))
    dispatcher.add_handler(CommandHandler("vieworders", view_orders))

    updater.start_polling()
    updater.idle()
