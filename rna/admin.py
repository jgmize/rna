from django.contrib import admin

from . import models

admin.site.register(models.Channel)
admin.site.register(models.Product)
admin.site.register(models.Tag)
admin.site.register(models.Note)
admin.site.register(models.Release)
