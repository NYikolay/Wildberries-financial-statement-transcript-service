# Generated by Django 4.1.4 on 2023-02-14 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_alter_salereport_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleobject',
            name='brand_name',
            field=models.CharField(max_length=125, null=True, verbose_name='Бренд'),
        ),
        migrations.AlterField(
            model_name='saleobject',
            name='nm_id',
            field=models.BigIntegerField(null=True, verbose_name='Артикул'),
        ),
        migrations.AlterField(
            model_name='saleobject',
            name='subject_name',
            field=models.CharField(max_length=125, null=True, verbose_name='Предмет'),
        ),
    ]
