# Generated by Django 4.1.4 on 2023-01-16 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_salereport_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_accepted_terms_of_offer',
            field=models.BooleanField(default=True, verbose_name='Согласен ли с условиями Оферты'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=11, verbose_name='Контактный номер телефона'),
        ),
    ]
