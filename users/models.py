from __future__ import unicode_literals

from django.db.models import Q, UniqueConstraint
from django.utils import timezone
from django.db import models
from django.core import validators
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from users.managers import UserManager


cyrillic_exclusion = RegexValidator(r'^[^а-яА-Я]*$', 'Символы кириллицы в API ключе недопустимы')


class UserRoles(models.TextChoices):
    admin = 'Admin'
    client = 'Client'
    moderator = 'Moderator'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True, validators=[validators.validate_email])
    first_name = models.CharField('Имя', max_length=30, blank=True)
    last_name = models.CharField('Фамилия', max_length=30, blank=True)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    phone = models.CharField(max_length=18, blank=True, verbose_name='Контактный номер телефона')
    is_accepted_terms_of_offer = models.BooleanField('Согласен ли с условиями Оферты')
    role = models.CharField(
        max_length=9,
        choices=UserRoles.choices,
        default=UserRoles.client,
        verbose_name='Роль пользователя'
    )
    is_active = models.BooleanField('active', default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['is_accepted_terms_of_offer']

    @property
    def is_staff(self):
        return self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class WBApiKey(models.Model):
    api_key = models.TextField(
        max_length=900,
        verbose_name='API ключ Wildberries',
        validators=[cyrillic_exclusion]
    )
    name = models.CharField(max_length=65, verbose_name='Название компании продавца')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keys', verbose_name='Пользователь')
    is_current = models.BooleanField(default=True, verbose_name='Является ли веб ключ текущим')
    is_wb_data_loaded = models.BooleanField(default=False, verbose_name='Загружен ли самый первый отчёт')
    is_products_loaded = models.BooleanField(default=False, verbose_name='Загружен ли первоначальный список товаров')
    last_reports_update = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления списка отчётов')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'API ключ пользователя {self.user}'

    class Meta:
        verbose_name = 'API ключ'
        verbose_name_plural = 'API ключи'
        ordering = ['user']
        constraints = [
            UniqueConstraint(fields=['is_current', 'user'], condition=Q(is_current=True),
                             name='unique_is_current'),
        ]

    # def clean(self):
    #     if WBApiKey.objects.filter(user=self.user).count() == 1:
    #         raise ValidationError('Для пользователя доступен только 1 api ключ')


class TaxRate(models.Model):
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.CASCADE,
        related_name='taxes',
        verbose_name='API ключ компании'
    )
    tax_rate = models.FloatField(default=0)
    commencement_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Ставка налога для {self.api_key.name}'

    class Meta:
        verbose_name = 'Ставка налога'
        verbose_name_plural = 'Ставки налога'
        ordering = ['commencement_date']


class ClientUniqueProduct(models.Model):
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.CASCADE,
        related_name='api_key_products',
        verbose_name='Апи ключ'
    )
    nm_id = models.BigIntegerField('Артикул')
    brand = models.CharField(max_length=65, verbose_name='Бренд')
    image = models.URLField(null=True, verbose_name='Картинка товара')
    product_name = models.CharField(max_length=125, null=True, verbose_name='Наименование товара')

    def __str__(self):
        return f'Товар {self.product_name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class NetCost(models.Model):
    product = models.ForeignKey(
        ClientUniqueProduct,
        on_delete=models.CASCADE,
        related_name='cost_prices',
        verbose_name='Продукт'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Значение себестоимости'
    )
    cost_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Себестоимость от {self.cost_date}'

    class Meta:
        verbose_name = 'Значение себестоимости'
        verbose_name_plural = 'Значения себестоимостей'


class SaleObject(models.Model):
    realizationreport_id = models.BigIntegerField('Номер отчёта')
    week_num = models.IntegerField('Номер недели')
    month_num = models.IntegerField('Номер месяца')
    year = models.IntegerField('Год продажи', null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales', verbose_name='Пользователь')
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.CASCADE,
        related_name='api_key_sales',
        verbose_name='Апи ключ'
    )
    date_from = models.DateTimeField('Дата начала отчетного периода')
    date_to = models.DateTimeField('Дата конца отчетного периода')
    create_dt = models.DateTimeField('Дата формирования отчёта')
    gi_id = models.BigIntegerField('Номер поставки')
    subject_name = models.CharField(max_length=125, verbose_name='Предмет')
    nm_id = models.BigIntegerField('Артикул')
    brand_name = models.CharField(max_length=125, verbose_name='Бренд')
    sa_name = models.CharField(max_length=65, verbose_name='Артикул поставщика')
    ts_name = models.CharField(max_length=65, verbose_name='Размер')
    barcode = models.CharField(max_length=125, verbose_name='Бар-код')
    doc_type_name = models.CharField(max_length=65, verbose_name='Тип документа')
    order_dt = models.DateTimeField('Дата заказа')
    sale_dt = models.DateTimeField('Дата продажи')
    quantity = models.IntegerField('Количество')
    retail_price = models.FloatField('Цена розничная')
    retail_price_withdisc_rub = models.FloatField('Цена розничная с учетом согласованной скидки')
    ppvz_for_pay = models.FloatField('К перечислению продавцу за реализованный товар')
    penalty = models.FloatField('Штрафы')
    additional_payment = models.FloatField('Доплаты')
    site_country = models.CharField(max_length=65, verbose_name='Страна продажи')
    office_name = models.CharField(max_length=65, null=True, verbose_name='Склад')
    srid = models.CharField(max_length=225, verbose_name='Уникальный идентификатор заказа')
    delivery_rub = models.FloatField('Стоимость логистики')
    rid = models.BigIntegerField('Уникальный идентификатор позиции заказа')
    supplier_oper_name = models.CharField(max_length=125, verbose_name='Обоснование для оплаты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания в базе данных')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления в базе данных')

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'

    def __str__(self):
        return f'Продажа {self.owner.email}, за отчётный период {self.create_dt}'


class SaleReport(models.Model):
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='api_key_reports',
        verbose_name='Апи ключ'
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name='Владелец отчёта')
    realizationreport_id = models.BigIntegerField('Номер отчёта')
    week_num = models.IntegerField('Номер недели')
    year = models.IntegerField('Год отчёта', null=True)
    unique_week_uuid = models.UUIDField()
    month_num = models.IntegerField('Номер месяца')
    create_dt = models.DateTimeField('Дата формирования отчёта')
    date_from = models.DateTimeField('Дата начала отчетного периода')
    date_to = models.DateTimeField('Дата конца отчетного периода')
    storage_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Стоимость хранения'
    )
    cost_paid_acceptance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Стоимость платной приёмки'
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Прочие удержания'
    )
    supplier_costs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Расходы поставщка'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания в базе данных')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления в базе данных')

    def __str__(self):
        return f'Отчёт за период {self.create_dt}'

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'






