from django.db import models
from users.models import UserData


class Transaction(models.Model):
    user = models.ForeignKey(
        UserData, on_delete=models.SET_NULL, null=True, verbose_name="User")
    amount = models.DecimalField(
        max_digits=18, decimal_places=9, verbose_name="TON amount")
    comment = models.CharField(
        max_length=64, verbose_name="Memo/tag/Comment", null=True)
    tx_id = models.CharField(max_length=256, unique=True)  # blockchain hash
    lt = models.CharField(max_length=64, verbose_name="Logical Time", null=True)

    price_per_ton = models.DecimalField(
        max_digits=18, decimal_places=2, null=True)  # snapshot of TON price
    price_currency = models.CharField(max_length=8, default="usd", null=True)

    paid_time = models.DateTimeField(
                auto_now_add=True, null=True)  # Created & Update Date
    is_delete = models.BooleanField(default=False)
    atomic_failed =models.BooleanField(default=False)

    class Meta:
        ordering = ['-paid_time']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.comment}"


class TonCursor(models.Model):
    key = models.CharField(max_length=32, unique=True)
    last_lt = models.BigIntegerField(default=0)
    
    def __str__(self):
        return f"{self.last_lt}"
    
    class Meta:
        verbose_name = "Ton Cursor"
        verbose_name_plural = "Ton Cursor"

