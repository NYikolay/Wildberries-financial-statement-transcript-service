# Generated by Django 4.1.4 on 2023-02-13 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_salereport_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salereport',
            options={'verbose_name': 'Отчёт', 'verbose_name_plural': 'Отчёты'},
        ),
    ]
