# Generated by Django 4.1.4 on 2023-01-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_salereport_storage_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salereport',
            name='cost_paid_acceptance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Стоимость платной приёмки'),
        ),
        migrations.AlterField(
            model_name='salereport',
            name='other_deductions',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Прочие удержания'),
        ),
        migrations.AlterField(
            model_name='salereport',
            name='supplier_costs',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Расходы поставщка'),
        ),
    ]
