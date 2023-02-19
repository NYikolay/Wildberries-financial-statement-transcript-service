from django.db import models

from users.models import User


class ContactMessageTypes(models.TextChoices):
    question = 'Задать вопрос'
    idea = 'Предложить идею'
    comment = 'Комментарий'
    error = 'Сообщить об ошибке'


class ContactMessage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='contact_messages',
        verbose_name='Пользователь'
    )
    message_type = models.CharField(max_length=18, choices=ContactMessageTypes.choices, verbose_name='Тип обращения')
    user_name = models.CharField(max_length=65, verbose_name='Имя пользователя')
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания обращения')

    class Meta:
        verbose_name = 'Обращение пользователя'
        verbose_name_plural = 'Обращения пользователей'

    def __str__(self):
        return f'Обращение по теме "{self.message_type}", от пользователя - {self.user.email}'


