# Generated by Django 4.1.7 on 2023-05-23 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0062_alter_saleobject_delivery_rub_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleobject',
            name='rid',
            field=models.BigIntegerField(null=True, verbose_name='Уникальный идентификатор позиции заказа'),
        ),
    ]
