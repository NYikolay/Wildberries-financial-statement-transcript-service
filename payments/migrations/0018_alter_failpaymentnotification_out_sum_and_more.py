# Generated by Django 4.1.7 on 2023-04-03 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_alter_failpaymentnotification_out_sum_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='failpaymentnotification',
            name='out_sum',
            field=models.DecimalField(decimal_places=7, max_digits=13, verbose_name='Стоимость подписки'),
        ),
        migrations.AlterField(
            model_name='subscriptiontype',
            name='cost',
            field=models.DecimalField(decimal_places=7, max_digits=13, verbose_name='Стоимость подписки'),
        ),
        migrations.AlterField(
            model_name='successpaymentnotification',
            name='out_sum',
            field=models.DecimalField(decimal_places=7, max_digits=13, verbose_name='Стоимость подписки'),
        ),
    ]
