from django.contrib import admin
from . import models


@admin.register(models.UserData)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    readonly_fields = ["id", "language"]
    search_fields = ["id", "username"]


@admin.register(models.BotSettings)
class BotSettingAdmin(admin.ModelAdmin):
    pass
