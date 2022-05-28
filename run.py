# -*- coding: utf-8 -*-
import os

import django

from carona_parque.bot.dispatcher import run_polling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carona_parque.settings")
django.setup()


if __name__ == "__main__":
    run_polling()
