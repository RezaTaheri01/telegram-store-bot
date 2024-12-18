from django.db import models
from users.models import UserData
from django.utils import timezone


# Create your models here.

class Transitions(models.Model):
    user = models.ForeignKey(to=UserData, on_delete=models.CASCADE, verbose_name="User", default=686588127)
    transitions_code = models.IntegerField(unique=True, blank=True, null=True)
    amount = models.IntegerField()
    paid_time = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

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
