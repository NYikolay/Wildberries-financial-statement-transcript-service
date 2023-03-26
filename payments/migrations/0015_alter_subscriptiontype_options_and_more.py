# Generated by Django 4.1.4 on 2023-03-22 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0014_alter_subscriptiontype_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptiontype',
            options={'ordering': ['cost'], 'verbose_name': 'Тип подписки', 'verbose_name_plural': 'Типы подписок'},
        ),
        migrations.AlterField(
            model_name='subscriptiontype',
            name='type',
            field=models.CharField(choices=[('Test', 'Test'), ('Start', 'Start'), ('Middle', 'Middle'), ('Long', 'Long')], max_length=10, verbose_name='Тип подписки'),
        ),
    ]
