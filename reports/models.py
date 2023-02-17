from django.db import models
from django.db.models import Q, UniqueConstraint


class InfoTypes(models.TextChoices):
    reports = 'reports_info'


class GeneralInformationObj(models.Model):
    info_type = models.CharField(max_length=25, choices=InfoTypes.choices, null=True, blank=True)
    info_message = models.CharField(max_length=625, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'Сообщение типа {self.info_type}'

    class Meta:
        verbose_name = 'Сообщение для пользователей'
        verbose_name_plural = 'Сообщения для пользователей'
        constraints = [
            UniqueConstraint(fields=['info_type', 'is_active'], condition=Q(is_active=True),
                             name='unique_is_active'),
        ]
