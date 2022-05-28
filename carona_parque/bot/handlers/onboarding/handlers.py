# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import CallbackContext


def hello(update: Update, context: CallbackContext):
    update.message.reply_text("Hello World!")
