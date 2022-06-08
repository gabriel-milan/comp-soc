# -*- coding: utf-8 -*-
from typing import List
from telegram import Update
from telegram.ext import CallbackContext

from carona_parque.bot.models import Neighborhood, Zone


def list_neighborhoods(update: Update, context: CallbackContext):
    # Get arguments (can have one or zero)
    if len(context.args) == 0:
        filter_zone = None
    elif len(context.args) == 1:
        try:
            filter_zone = Zone.objects.get(id=context.args[0])
        except Zone.DoesNotExist:
            update.message.reply_text(
                "A zona especificada não existe. Use /zonas para ver a lista de zonas."
            )
            return
    else:
        update.message.reply_text(
            "Você deve digitar `/vizinhancas <id-da-zona>` ou somente `/vizinhancas`"
        )
        return
    # Get neighborhoods
    neighborhoods: List[Neighborhood] = (
        Neighborhood.objects.filter(
            zone=filter_zone,
        )
        if filter_zone
        else Neighborhood.objects.all()
    )
    base_text = "*Lista de vizinhanças*\n\n" + "\n".join(
        f" * {n.id} - {n.name} (Zona {n.zone.id} - {n.zone.name})"
        for n in neighborhoods
    )
    if not filter_zone:
        base_text += "\n\n*Para filtrar por zona, digite `/vizinhancas <id-da-zona>`"
    update.message.reply_text(base_text)


def list_zones(update: Update, context: CallbackContext):
    zones: List[Zone] = Zone.objects.all()
    update.message.reply_text(
        "*Lista de zonas*\n\n" + "\n".join(f" * {z.id} - {z.name}" for z in zones)
    )
