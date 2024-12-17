from django.contrib import admin
from . import models


# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    readonly_fields = ['id']


admin.site.register(models.UserData, AccountAdmin)
