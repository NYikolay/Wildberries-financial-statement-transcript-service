# Generated by Django 4.2.5 on 2023-11-30 12:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0072_merge_20231130_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='promocodes', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
    ]
