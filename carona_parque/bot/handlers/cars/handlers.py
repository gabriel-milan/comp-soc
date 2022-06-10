# -*- coding: utf-8 -*-
import re

from telegram import Update
from telegram.ext import CallbackContext

from carona_parque.bot.models import Car, User


class UserNotApproved(Exception):
    pass


def add_car(update: Update, context: CallbackContext):
    # Get chat ID
    chat_id = update.effective_chat.id

    # Get user
    try:
        user: User = User.objects.get(telegram_chat_id=chat_id)
        if not user.approved:
            raise UserNotApproved()
    except User.DoesNotExist:
        # tell it's not registered
        update.message.reply_text(
            "Você ainda não está Cadastrado! 😓 Se deseja se cadastrar, digite `/cadastrar <nome>`"
        )
        return
    except UserNotApproved:
        update.message.reply_text("Você ainda não está aprovado. Mas fique de olho! 🧐")
        return

    # Get arguments (should have model, color and plate)
    if len(context.args) != 3:
        update.message.reply_text(
            "Você deve digitar `/adicionar <modelo> <cor> <placa>`"
        )
        return
    model = context.args[0]
    color = context.args[1]
    plate = context.args[2]

    # Validate arguments
    if not model:
        update.message.reply_text(
            "Você deve digitar `/adicionar <modelo> <cor> <placa>`"
        )
        return
    if not color:
        update.message.reply_text(
            "Você deve digitar `/adicionar <modelo> <cor> <placa>`"
        )
        return
    if not plate:
        update.message.reply_text(
            "Você deve digitar `/adicionar <modelo> <cor> <placa>`"
        )
        return
    if len(plate) != 7:
        update.message.reply_text("A placa deve ter 7 caracteres no formato `ABC1234`")
        return
    if not re.match(r"^[a-zA-Z]{3}[0-9][a-jA-J0-9][0-9]{2}$", plate):
        update.message.reply_text("A placa deve ter 7 caracteres no formato `ABC1234`")
        return

    # Check if car already exists
    try:
        car: Car = Car.objects.get(plate=plate)
        update.message.reply_text(f"Já existe um carro com a placa `{plate}`! 😢")
        return
    except Car.DoesNotExist:
        pass

    # Create car
    car = Car.objects.create(user=user, model=model, color=color, plate=plate)
    update.message.reply_text(
        f"Carro adicionado com sucesso! 😃\n\n"
        f"Modelo: {model}\n"
        f"Cor: {color}\n"
        f"Placa: {plate}\n"
        f"ID: {car.id}"
    )


def list_cars(update: Update, context: CallbackContext):
    # Get chat ID
    chat_id = update.effective_chat.id

    # Get user
    try:
        user: User = User.objects.get(telegram_chat_id=chat_id)
        if not user.approved:
            raise UserNotApproved()
    except User.DoesNotExist:
        # tell it's not registered
        update.message.reply_text(
            "Você ainda não está cadastrado! 😓 Se deseja se cadastrar, digite `/cadastrar <nome>`"
        )
        return
    except UserNotApproved:
        update.message.reply_text("Você ainda não está aprovado. Mas fique de olho! 🧐")
        return

    # Get cars
    cars = Car.objects.filter(user=user)

    # Check if there are cars
    if not cars:
        update.message.reply_text("Você não tem nenhum carro cadastrado! 😢")
        return

    # Send message with cars
    update.message.reply_text(
        "Você tem os seguintes carros cadastrados:\n"
        "ID\tModelo\tCor\tPlaca\n"
        "----------------------------------------------------\n"
        "{}".format(
            "\n".join(
                [f"{car.id}\t{car.model}\t{car.color}\t{car.plate}" for car in cars]
            )
        )
    )
