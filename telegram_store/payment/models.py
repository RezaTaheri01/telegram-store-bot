from django.db import models
from users.models import UserData
from django.utils import timezone
from bot_settings import valid_link_in_seconds


# Create your models here.

class Transitions(models.Model):
    user = models.ForeignKey(to=UserData, on_delete=models.CASCADE, verbose_name="User")
    transitions_code = models.IntegerField(unique=True, blank=True, null=True)
    amount = models.IntegerField()
    paid_time = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['-paid_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='amount_positive'
            )
        ]
        verbose_name_plural = "Transitions"
        verbose_name = "Transition"

    def mark_as_paid(self):
        self.is_paid = True
        self.paid_time = timezone.now()
        self.save()

    def is_expired(self):
        if (timezone.now() - self.created_date).total_seconds() > valid_link_in_seconds:  # 1 hour:
            self.is_delete = True
            self.save()
            return True
        return False
