from django.db import models
from users.models import UserData


# Create your models here.

class Transitions(models.Model):
    transitions_code = models.IntegerField(unique=True, blank=True, null=True)
    amount = models.IntegerField()
    data_time = models.DateTimeField(null=True, blank=True)
    is_payed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='amount_positive'
            )
        ]
        verbose_name_plural = "Transitions"
        verbose_name = "Transition"

    def mark_as_paid(self):
        self.is_payed = True
        self.save()
