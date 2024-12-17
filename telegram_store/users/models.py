from django.db import models


# Create your models here.
class UserData(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)  # Telegram user ID
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)  # null because it may be hidden
    username = models.CharField(max_length=100, unique=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = "User Data"
        verbose_name_plural = "Users Data"
