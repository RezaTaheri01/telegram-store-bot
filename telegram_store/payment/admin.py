from django.contrib import admin
from . import models


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "paid_time", "is_delete")
    list_filter = ("paid_time", "is_delete")
    readonly_fields = ("user",
                       "amount",
                       "comment",
                       "tx_id",
                       "price_per_ton",
                       "price_currency",
                       "paid_time",
                       "lt"
                       )
    search_fields = ("user__id", "user__username", "tx_id", "comment", "lt")

@admin.register(models.TonCursor)
class TonCursorAdmin(admin.ModelAdmin):
   readonly_fields = ("key",)
