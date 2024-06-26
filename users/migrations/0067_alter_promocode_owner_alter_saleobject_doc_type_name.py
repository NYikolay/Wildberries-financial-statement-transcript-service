# Generated by Django 4.2.5 on 2023-10-03 12:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0066_promocode_discount_percent_alter_user_promocode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promocodes', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='saleobject',
            name='doc_type_name',
            field=models.CharField(max_length=65, null=True, verbose_name='Тип документа'),
        ),
    ]
