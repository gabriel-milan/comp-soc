# -*- coding: utf-8 -*-
from django.conf import settings
from telegram import Bot, BotCommand, Update
from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, Updater

from carona_parque.celery import app
from carona_parque.bot.handlers.default import handle
from carona_parque.bot.handlers.cars import handlers as cars_handlers
from carona_parque.bot.handlers.onboarding import handlers as onboarding_handlers

COMMANDS = {
    "cadastro": {
        "description": "Verifica o estado do seu cadastro",
        "handler": onboarding_handlers.registration_status,
    },
    "cadastrar": {
        "description": "Faz o cadastro do usuário",
        "handler": onboarding_handlers.register,
    },
    "adicionar_carro": {
        "description": "Adiciona um carro ao usuário",
        "handler": cars_handlers.add_car,
    },
    "carros": {
        "description": "Lista os carros do usuário",
        "handler": cars_handlers.list_cars,
    },
}


def setup_dispatcher(dispatcher: Dispatcher):
    for command, command_data in COMMANDS.items():
        dispatcher.add_handler(CommandHandler(command, command_data["handler"]))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
    return dispatcher


def setup_commands(bot: Bot):
    bot.set_my_commands(
        commands=[
            BotCommand(command, command_data["description"])
            for command, command_data in COMMANDS.items()
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
