# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import CallbackContext

from carona_parque.bot.models import User


def register(update: Update, context: CallbackContext):
    # Get chat ID
    chat_id = update.effective_chat.id

    # Get user
    try:
        User.objects.get(telegram_chat_id=chat_id)
        update.message.reply_text(
            "Você já está cadastrado! Para verificar o estado do seu cadastro, digite /cadastro"
        )
    except User.DoesNotExist:
        # Get username
        username = update.message.from_user.username
        # Assert arguments length
        if len(context.args) != 1:
            update.message.reply_text("Você deve digitar `/cadastrar <primeiro-nome>`")
            return
        # Get arguments
        name = context.args[0]
        # Create user
        User.objects.create(
            telegram_chat_id=chat_id,
            telegram_username=username,
            name=name,
        )
        # Send message
        update.message.reply_text(
            (
                "Você foi cadastrado com sucesso! Para verificar o estado do seu cadastro, ",
                "digite /cadastro",
            )
        )


def registration_status(update: Update, context: CallbackContext):
    # Get chat ID
    chat_id = update.effective_chat.id

    # Get user
    try:
        user: User = User.objects.get(telegram_chat_id=chat_id)
        if user.approved:
            update.message.reply_text("Você já está cadastrado e aprovado! 🤗")
            return
        else:
            update.message.reply_text(
                "Você ainda não está aprovado. Mas fique de olho! 🧐"
            )
    except User.DoesNotExist:
        # tell it's not registered
        update.message.reply_text(
            "Você ainda não está cadastrado! 😓 Se deseja se cadastrar, digite `/cadastrar <nome>`"
        )
