# Generated by Django 4.1.4 on 2023-02-13 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_alter_user_phone'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salereport',
            options={'ordering': ['-realizationreport_id'], 'verbose_name': 'Отчёт', 'verbose_name_plural': 'Отчёты'},
        ),
    ]
