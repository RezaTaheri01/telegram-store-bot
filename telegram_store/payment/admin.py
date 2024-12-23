from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Transitions)
class TransitionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'transitions_code', 'amount', 'paid_time', 'is_paid', 'created_date')
    list_filter = ('is_paid', 'paid_time')
    search_fields = ('transitions_code',)
