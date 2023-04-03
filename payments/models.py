from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators


class SubscriptionTypes(models.TextChoices):
    TEST = _('Test')
    START = _('Start')
    MIDDLE = _('Middle')
    LONG = _('Long')


# !IMPORTANT. When changing DURATION_DESCRIPTION_CHOICES pay
# attention to the function payments.services.generating_subscribed_to_date and users.views.ConfirmRegistrationView
DURATION_DESCRIPTION_CHOICES = [
    ('Недели', (
        ('неделя', 'Неделя'),
        ('недели', 'Недели'),
        ('недель', 'Недель'),
    )
     ),
    ('Месяца', (
        ('месяц', 'Месяц'),
        ('месяца', 'Месяца'),
        ('месяцев', 'Месяцев')
    )
     )
]


class SubscriptionType(models.Model):
    type = models.CharField('Тип подписки', max_length=10, choices=SubscriptionTypes.choices)
    duration = models.IntegerField('Длительность подписки')
    duration_desc = models.CharField(
        'Строковое описание длительности (месяц, год)',
        max_length=10,
        choices=DURATION_DESCRIPTION_CHOICES
    )
    cost = models.DecimalField('Стоимость подписки', max_digits=13, decimal_places=7)
    build_in_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Процент скидки')

    def __str__(self):
        return f'Стоимость: {self.cost}, длительность: {self.duration} {self.duration_desc}'

    class Meta:
        verbose_name = 'Тип подписки'
        verbose_name_plural = 'Типы подписок'
        ordering = ['cost']


class SuccessPaymentNotification(models.Model):
    inv_id = models.IntegerField('Номер успешного заказа', db_index=True)
    out_sum = models.DecimalField('Стоимость подписки', max_digits=13, decimal_places=7)

    created_at = models.DateTimeField('Дата и время получения уведомления', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление об успешном платеже'
        verbose_name_plural = 'Уведомления об успешных платежах'

    def __str__(self):
        return 'Номер - {}, сумма - {} ({})'.format(self.inv_id, self.out_sum, self.created_at)


class FailPaymentNotification(models.Model):
    inv_id = models.IntegerField('Номер отмененного заказа', db_index=True)
    out_sum = models.DecimalField('Стоимость подписки', max_digits=13, decimal_places=7)

    created_at = models.DateTimeField('Дата и время получения уведомления', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление об отменённом платеже'
        verbose_name_plural = 'Уведомления об отменённых платежах'

    def __str__(self):
        return 'Номер - {}, сумма - {} ({})'.format(self.inv_id, self.out_sum, self.created_at)



