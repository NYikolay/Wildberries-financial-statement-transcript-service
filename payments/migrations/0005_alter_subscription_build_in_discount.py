# Generated by Django 4.1.4 on 2023-03-14 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_alter_subscription_build_in_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='build_in_discount',
            field=models.IntegerField(blank=True, null=True, verbose_name='Заложенная в тариф скидка'),
        ),
    ]
