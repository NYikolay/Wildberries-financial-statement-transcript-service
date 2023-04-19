# Generated by Django 4.1.7 on 2023-04-03 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0049_alter_wbapikey_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid_sum',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='total_cost',
            field=models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Окончательная стоимость подписки'),
        ),
    ]