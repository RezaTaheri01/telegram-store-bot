from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Transitions)
class TransitionsAdmin(admin.ModelAdmin):
    list_display = ('transitions_code', 'amount', 'data_time', 'is_payed')
    list_filter = ('is_payed', 'data_time')
    search_fields = ('transitions_code',)
