from __future__ import unicode_literals
from datetime import datetime

from django.dispatch import receiver
from django.db.models import Q, UniqueConstraint
from django.db import models
from django.core import validators
from payments.signals import result_received, fail_payment_signal
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import RegexValidator

from payments.models import SubscriptionType
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

    @property
    def is_subscribed(self):
        return UserSubscription.objects.filter(
            user=self,
            subscribed_to__gt=datetime.now()
        ).exists()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Order(models.Model):
    paid_sum = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True, default='processed')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Клиент'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')

    def __str__(self):
        return f'Покупка подписки. Статус оплаты - {self.status}'

    class Meta:
        verbose_name = 'Статус покупки подписки'
        verbose_name_plural = 'Статусы покупки подписки'


@receiver(result_received)
def payment_received(sender, **kwargs):
    order = Order.objects.get(pk=kwargs['InvId'])
    order.status = 'paid'
    order.paid_sum = kwargs['OutSum']
    order.save()


@receiver(fail_payment_signal)
def payment_failed(sender, **kwargs):
    order = Order.objects.get(pk=kwargs['InvId'])
    order.status = 'fail'
    order.paid_sum = kwargs['OutSum']
    order.save()


class UserSubscription(models.Model):
    subscription_type = models.ForeignKey(
        SubscriptionType,
        on_delete=models.PROTECT,
        null=True,
        related_name='subscriptions',
        verbose_name='Тип подписки'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    subscribed_from = models.DateTimeField('Дата оформления подписки')
    total_cost = models.DecimalField('Окончательная стоимость подписки', max_digits=13, decimal_places=7)
    subscribed_to = models.DateTimeField('Дата окончания подписки')
    discount_percent = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Процент скидки')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Подписка пользователя {self.user.email}'

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'


class UserDiscount(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discounts',
        verbose_name='Пользователь'
    )
    percent = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Процент скидки')
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'Скидка на подписку пользователя: {self.user.email}'

    class Meta:
        verbose_name = 'Скидка пользователя'
        verbose_name_plural = 'Скидки пользователей'
        constraints = [
            UniqueConstraint(
                fields=['is_active', 'user'],
                condition=Q(is_active=True),
                name='unique_user_active_discount_priority')
        ]


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
    is_active_import = models.BooleanField(default=False, verbose_name='Происходит ли загрузка отчёта')
    last_reports_update = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления списка отчётов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания ключа')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Ключ пользователя {self.user}'

    class Meta:
        verbose_name = 'API ключ'
        verbose_name_plural = 'API ключи'
        ordering = ['user']
        constraints = [
            UniqueConstraint(fields=['is_current', 'user'], condition=Q(is_current=True),
                             name='unique_is_current'),
        ]


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
    nm_id = models.BigIntegerField('Артикул', unique=True)
    brand = models.CharField(max_length=65, verbose_name='Бренд')
    image = models.URLField(null=True, verbose_name='Картинка товара')
    product_name = models.CharField(max_length=125, null=True, verbose_name='Наименование товара')

    def __str__(self):
        return f'Товар {self.product_name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        index_together = [
            ("image", "product_name")
        ]


class NetCost(models.Model):
    product = models.ForeignKey(
        ClientUniqueProduct,
        on_delete=models.CASCADE,
        related_name='cost_prices',
        verbose_name='Продукт'
    )
    amount = models.DecimalField(
        max_digits=13,
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
    product = models.ForeignKey(
        ClientUniqueProduct,
        on_delete=models.CASCADE,
        null=True,
        related_name='product_sales',
        verbose_name='Товар'
    )
    date_from = models.DateTimeField('Дата начала отчетного периода')
    date_to = models.DateTimeField('Дата конца отчетного периода')
    create_dt = models.DateTimeField('Дата формирования отчёта')
    gi_id = models.BigIntegerField('Номер поставки')
    subject_name = models.CharField(max_length=125, verbose_name='Предмет', null=True)
    nm_id = models.BigIntegerField('Артикул', null=True)
    brand_name = models.CharField(max_length=125, verbose_name='Бренд', null=True)
    sa_name = models.CharField(max_length=65, verbose_name='Артикул поставщика', null=True)
    ts_name = models.CharField(max_length=65, verbose_name='Размер', null=True)
    barcode = models.CharField(max_length=125, verbose_name='Бар-код')
    doc_type_name = models.CharField(max_length=65, verbose_name='Тип документа')
    order_dt = models.DateTimeField('Дата заказа', null=True)
    sale_dt = models.DateTimeField('Дата продажи', null=True)
    quantity = models.IntegerField('Количество')
    retail_price = models.FloatField('Цена розничная')
    retail_price_withdisc_rub = models.FloatField('Цена розничная с учетом согласованной скидки', null=True)
    ppvz_for_pay = models.FloatField('К перечислению продавцу за реализованный товар')
    penalty = models.FloatField('Штрафы')
    additional_payment = models.FloatField('Доплаты')
    site_country = models.CharField(max_length=65, verbose_name='Страна продажи', null=True)
    office_name = models.CharField(max_length=65, null=True, verbose_name='Склад')
    srid = models.CharField(max_length=225, verbose_name='Уникальный идентификатор заказа', null=True)
    delivery_rub = models.FloatField('Стоимость логистики', null=True)
    rid = models.BigIntegerField('Уникальный идентификатор позиции заказа', null=True)
    supplier_oper_name = models.CharField(max_length=125, verbose_name='Обоснование для оплаты')
    rrd_id = models.BigIntegerField('Номер строки', null=True)
    retail_amount = models.FloatField('Сумма продаж (возвратов)')
    sale_percent = models.IntegerField('Согласованная скидка', null=True)
    commission_percent = models.FloatField('Процент комиссии', null=True)
    rr_dt = models.DateTimeField('Дата операции', null=True)
    shk_id = models.BigIntegerField('Штрих-код', null=True)
    delivery_amount = models.IntegerField('Количество доставок', null=True)
    return_amount = models.IntegerField('Количество возвратов', null=True)
    gi_box_type_name = models.CharField(max_length=40, verbose_name='Тип коробов', null=True)
    product_discount_for_report = models.FloatField('Согласованный продуктовый дисконт', null=True)
    supplier_promo = models.FloatField('Промокод', null=True)
    ppvz_spp_prc = models.FloatField('Скидка постоянного покупателя', null=True)
    ppvz_kvw_prc_base = models.FloatField('Размер кВВ без НДС, % базовый', null=True)
    ppvz_kvw_prc = models.FloatField('Итоговый кВВ без НДС, %', null=True)
    ppvz_sales_commission = models.FloatField('Вознаграждение с продаж до вычета услуг поверенного, без НДС', null=True)
    ppvz_reward = models.FloatField('Возмещение за выдачу и возврат товаров на ПВЗ', null=True)
    acquiring_fee = models.FloatField('Возмещение расходов по эквайрингу', null=True)
    acquiring_bank = models.CharField(
        max_length=40,
        verbose_name='Наименование банка, предоставляющего услуги эквайринга',
        null=True
    )
    ppvz_vw = models.FloatField('Вознаграждение WB без НДС', null=True)
    ppvz_vw_nds = models.FloatField('НДС с вознаграждения WB', null=True)
    ppvz_office_id = models.IntegerField('Номер офиса', null=True)
    ppvz_office_name = models.CharField(max_length=40, verbose_name='Наименование офиса доставки', null=True)
    ppvz_supplier_id = models.BigIntegerField('Номер партнера', null=True)
    ppvz_supplier_name = models.CharField(max_length=125, verbose_name='Партнёр', null=True)
    ppvz_inn = models.CharField(max_length=50, verbose_name='ИНН партнера', null=True)
    declaration_number = models.CharField(max_length=50, verbose_name='Номер таможенной декларации', null=True)
    bonus_type_name = models.TextField('Обоснование штрафов и доплат', null=True)
    sticker_id = models.CharField(max_length=40, verbose_name='Цифровое значение стикера', null=True)
    kiz = models.TextField('Код маркировки', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания в базе данных')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления в базе данных')

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        index_together = [
            ("year", "week_num"),
            ("barcode", "nm_id")
        ]

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
        max_digits=13,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Стоимость хранения'
    )
    cost_paid_acceptance = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Стоимость платной приёмки'
    )
    other_deductions = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Прочие удержания'
    )
    supplier_costs = models.DecimalField(
        max_digits=13,
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


class IncorrectReport(models.Model):
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name='unavailable_api_key_reports',
        verbose_name='Api ключ'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='unavailable_reports',
        verbose_name='Владелец отчёта'
    )
    realizationreport_id = models.BigIntegerField('Номер отчёта')
    date_from = models.DateTimeField('Дата начала отчетного периода')
    date_to = models.DateTimeField('Дата конца отчетного периода')

    def __str__(self):
        return f'Некорректный отчёт пользователя {self.owner.email}'

    class Meta:
        verbose_name = 'Некорректный отчёт'
        verbose_name_plural = 'Некорректные отчёты'


class UnloadedReports(models.Model):
    api_key = models.ForeignKey(
        WBApiKey,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name='unloaded_reports',
        verbose_name='Api ключ'
    )
    realizationreport_id = models.BigIntegerField('Номер отчёта')

    def __str__(self):
        return f'Недозагруженный отчёт пользователя - {self.api_key.user.email}'

    class Meta:
        verbose_name = 'Недозагруженный отчёт'
        verbose_name_plural = 'Недозагруженные отчёты'


