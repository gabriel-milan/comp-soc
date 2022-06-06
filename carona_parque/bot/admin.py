# -*- coding: utf-8 -*-
from django.contrib import admin

from carona_parque.bot.models import User, CarColor, Car, Zone, Neighborhood, Ride

admin.site.register(User)
admin.site.register(CarColor)
admin.site.register(Car)
admin.site.register(Zone)
admin.site.register(Neighborhood)
admin.site.register(Ride)
