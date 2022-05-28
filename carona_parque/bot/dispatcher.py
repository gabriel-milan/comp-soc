# -*- coding: utf-8 -*-
from django.conf import settings
from telegram import Bot, BotCommand, Update
from telegram.ext import CommandHandler, Dispatcher, Updater

from carona_parque.celery import app
from carona_parque.bot.handlers.onboarding import handlers as onboarding_handlers


def setup_dispatcher(dispatcher: Dispatcher):
    dispatcher.add_handler(CommandHandler("hello", onboarding_handlers.hello))
    return dispatcher


def setup_commands(bot: Bot):
    commands = {
        "hello": "Say hello to the bot",
    }
    bot.set_my_commands(
        commands=[
            BotCommand(command, description)
            for command, description in commands.items()
        ]
    )


def run_polling():
    updater = Updater(settings.TELEGRAM_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    dispatcher = setup_dispatcher(dispatcher)
    updater.start_polling()
    setup_commands(updater.bot)
    updater.idle()


bot = Bot(token=settings.TELEGRAM_TOKEN)
setup_commands(bot)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


dispatcher = setup_dispatcher(
    Dispatcher(
        bot, update_queue=None, workers=settings.TELEGRAM_WORKERS, use_context=True
    )
)
