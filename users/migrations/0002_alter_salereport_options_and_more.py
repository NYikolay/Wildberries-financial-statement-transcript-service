# Generated by Django 4.1.4 on 2023-01-15 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salereport',
            options={'ordering': ['-create_dt'], 'verbose_name': 'Отчёт', 'verbose_name_plural': 'Отчёты'},
        ),
        migrations.RemoveField(
            model_name='clientuniqueproduct',
            name='client',
        ),
        migrations.RemoveField(
            model_name='salereport',
            name='owner',
        ),
    ]
