# Generated by Django 4.1.4 on 2023-03-15 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_subscriptiontype_delete_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptiontype',
            name='build_in_discount',
            field=models.IntegerField(default=0, verbose_name='Заложенная в тариф скидка'),
        ),
    ]
