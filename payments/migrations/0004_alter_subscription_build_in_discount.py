# Generated by Django 4.1.4 on 2023-03-14 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='build_in_discount',
            field=models.IntegerField(blank=True, verbose_name='Заложенная в тариф скидка'),
        ),
    ]
