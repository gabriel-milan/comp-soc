# -*- coding: utf-8 -*-
from datetime import datetime, tzinfo
import re

from django.conf import settings
import pytz
from telegram import Update
from telegram.ext import CallbackContext

from carona_parque.bot.models import Car, Neighborhood, Ride, User, Zone
from carona_parque.bot.utils import smart_split


class UserNotApproved(Exception):
    pass


def add_ride(update: Update, context: CallbackContext):
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

    # Get arguments (must be car_id, neighborhood_id, date, time, seats)
    args = context.args
    if len(args) != 6:
        update.message.reply_text(
            "Você deve usar o comando `/adicionar_carona <id_carro> "
            + "<id_vizinhanca> <data> <hora> <vagas> <preco>`"  # noqa
        )
        return

    # Parse types
    try:
        car_id = int(args[0])
    except ValueError:
        update.message.reply_text("O id do carro deve ser um número inteiro.")
        return
    try:
        neighborhood_id = int(args[1])
    except ValueError:
        update.message.reply_text("O id da vizinhança deve ser um número inteiro.")
        return
    date = args[2]
    time = args[3]
    try:
        seats = int(args[4])
    except ValueError:
        update.message.reply_text("A quantidade de vagas deve ser um número inteiro.")
        return
    try:
        price = float(args[5])
    except ValueError:
        update.message.reply_text("O preço deve ser um número real.")
        return

    # Get car
    try:
        car: Car = Car.objects.get(id=car_id)
        assert car.user == user
    except Car.DoesNotExist:
        update.message.reply_text(
            "Você não pode adicionar caronas carros que não são seus! "
            + "Para ver a lista de carros, use /carros."  # noqa
        )
        return
    except AssertionError:
        update.message.reply_text(
            "Você não pode adicionar caronas carros que não são seus! "
            + "Para ver a lista de carros, use /carros."  # noqa
        )
        return

    # Get neighborhood
    try:
        neighborhood: Neighborhood = Neighborhood.objects.get(id=neighborhood_id)
    except Neighborhood.DoesNotExist:
        update.message.reply_text(
            "A vizinhança especificada não existe. Use /vizinhancas para ver a "
            + "lista de vizinhancas."  # noqa
        )
        return

    # Parse date (must be in format DD/MM/YYYY)
    try:
        date_parts = re.match(r"(\d{2})/(\d{2})/(\d{4})", date).groups()
        date: datetime = datetime(
            int(date_parts[2]),
            int(date_parts[1]),
            int(date_parts[0]),
            tzinfo=pytz.timezone(settings.TIME_ZONE),
        )
    except AttributeError:
        update.message.reply_text("A data deve estar no formato DD/MM/YYYY")

    # Parse time (must be in format HH:MM)
    try:
        time_parts = re.match(r"(\d{2}):(\d{2})", time).groups()
        date = date.replace(hour=int(time_parts[0]), minute=int(time_parts[1]))
    except AttributeError:
        update.message.reply_text("A hora deve estar no formato HH:MM")

    # Assert that date is in the future
    if date < datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
        update.message.reply_text("A data deve ser no futuro!")
        return

    # Create ride
    ride = Ride(
        car=car,
        destination=neighborhood,
        passenger_seats=seats,
        start_timestamp=date,
        price=price,
    )
    ride.save()

    # Send message
    update.message.reply_text("Carona adicionada com sucesso! 🎉")


def list_rides(update: Update, context: CallbackContext):
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

    # Check if there are arguments. There must be 0, 1 or 2 arguments
    if len(context.args) > 2:
        update.message.reply_text(
            "Você deve usar o comando `/listar_caronas` sem argumentos ou fornecendo a data "
            + "da carona e/ou o ID da zona."  # noqa
        )
        return

    # Parse arguments
    date = None
    zone = None
    if len(context.args) > 0:
        # Try to parse useful things from arguments
        for arg in context.args:
            try:
                date_parts = re.match(r"(\d{2})/(\d{2})/(\d{4})", arg).groups()
                date: datetime = datetime(
                    int(date_parts[2]),
                    int(date_parts[1]),
                    int(date_parts[0]),
                    tzinfo=pytz.timezone(settings.TIME_ZONE),
                )
            except AttributeError:
                pass
            try:
                zone = Zone.objects.get(id=int(arg))
            except Zone.DoesNotExist:
                pass
            except ValueError:
                pass
        # If there is no date and no zone, it's an error
        if date is None and zone is None:
            update.message.reply_text(
                "Você deve usar o comando `/listar_caronas` sem argumentos ou fornecendo a data "
                + "da carona e/ou o ID da zona."  # noqa
            )
            return

    # If there's a date, assure it's in the future
    if date is not None and date < datetime.now(tz=pytz.timezone(settings.TIME_ZONE)):
        update.message.reply_text("A data deve ser no futuro!")
        return

    # Start text
    base_text = ""

    # Get current datetime
    now = datetime.now(tz=pytz.UTC)

    # Get rides you're driving
    rides_driving = Ride.objects.filter(car__user=user).filter(start_timestamp__gte=now)
    if rides_driving:
        base_text += "Você irá dirigir:\n\n"
        for ride in rides_driving:
            base_text += (
                "=> "
                + ride.start_timestamp.astimezone(  # noqa
                    pytz.timezone(settings.TIME_ZONE)
                ).strftime("%d/%m/%Y %H:%M")
                + "\n"  # noqa
            )
            base_text += "    * Carro: " + str(ride.car) + "\n"
            base_text += "    * Vizinhança de destino: " + ride.destination.name + "\n"
            base_text += "    * Vagas totais: " + str(ride.passenger_seats) + "\n"
            base_text += (
                "    * Vagas disponíveis: "
                + str(ride.passenger_seats - ride.passengers.count())  # noqa
                + "\n"  # noqa
            )
            base_text += "    * Preço: " + str(ride.price) + "\n\n"

    # Get other rides
    rides_all = Ride.objects.filter(start_timestamp__gte=now)
    if date:
        rides_all = rides_all.filter(start_timestamp__date=date)
    if zone:
        rides_all = rides_all.filter(destination__zone=zone)
    other_rides_count = 0
    if rides_all:
        for ride in rides_all:
            if ride not in rides_driving:
                if other_rides_count == 0:
                    base_text += "Todas as caronas:\n\n"
                base_text += (
                    "=> "
                    + ride.start_timestamp.astimezone(  # noqa
                        pytz.timezone(settings.TIME_ZONE)
                    ).strftime("%d/%m/%Y %H:%M")
                    + "\n"  # noqa
                )
                base_text += "    * Carro: " + str(ride.car) + "\n"
                base_text += (
                    "    * Vizinhança de destino: " + ride.destination.name + "\n"
                )
                base_text += "    * Vagas totais: " + str(ride.passenger_seats) + "\n"
                base_text += (
                    "    * Vagas disponíveis: "
                    + str(ride.passenger_seats - ride.passengers.count())  # noqa
                    + "\n"  # noqa
                )
                base_text += "    * Preço: " + str(ride.price) + "\n\n"
                other_rides_count += 1

    # Send message
    if not base_text:
        update.message.reply_text("Não existem caronas cadastradas!")
    else:
        messages = smart_split(base_text, separator="\n\n")
        for i, message in enumerate(messages):
            if i == 0:
                update.message.reply_text(message)
            else:
                context.bot.send_message(chat_id=chat_id, text=message)
