from django.db import models


# Create your models here.
class UserData(models.Model):
    class LanguageChoices(models.TextChoices):
        english = 'en',
        farsi = 'fa'

    id = models.IntegerField(primary_key=True, unique=True)  # Telegram user ID
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    mobile_number = models.CharField(max_length=16, null=True, blank=True)  # null because it may be hidden
    username = models.CharField(max_length=64, null=True, blank=True)  # telegram check username to be unique
    balance = models.IntegerField(default=0)
    language = models.CharField(max_length=8, default='en', choices=LanguageChoices.choices,
                                verbose_name='Language')

    def __str__(self):
        if self.username:
            return f"{self.username}"
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    class Meta:
        verbose_name = "User Data"
        verbose_name_plural = "Users Data"
