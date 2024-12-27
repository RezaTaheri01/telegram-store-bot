from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Transactions)
class TransitionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_code', 'amount', 'paid_time', 'is_paid', 'created_date')
    list_filter = ('is_paid', 'paid_time')
    search_fields = ('transaction_code',)
