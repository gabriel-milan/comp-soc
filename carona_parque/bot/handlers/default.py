# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import CallbackContext


def handle(update: Update, context: CallbackContext):
    update.message.reply_text("Não entendi! 😢 Tente usar um dos comandos disponíveis.")
