# Generated by Django 4.2.5 on 2023-11-08 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0067_incorrectreport_create_dt_incorrectreport_week_num_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='netcost',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=13, verbose_name='Значение себестоимости'),
            preserve_default=False,
        ),
    ]
