# Generated by Django 4.1.4 on 2023-01-19 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_wbapikey_last_reports_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='netcost',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Расходы поставщка'),
        ),
        migrations.AlterField(
            model_name='netcost',
            name='cost_date',
            field=models.DateField(),
        ),
    ]
