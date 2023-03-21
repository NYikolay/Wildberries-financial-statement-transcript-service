# Generated by Django 4.1.4 on 2023-03-16 15:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_alter_order_options_order_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='customer_email',
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Клиент'),
        ),
    ]