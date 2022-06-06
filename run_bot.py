# -*- coding: utf-8 -*-
import os

import django
from loguru import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carona_parque.settings")
logger.info("Starting Django...")
django.setup()
logger.info("Django started!")


if __name__ == "__main__":
    from carona_parque.bot.dispatcher import run_polling

    logger.info("Starting bot...")
    run_polling()
