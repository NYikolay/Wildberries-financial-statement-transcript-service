# Generated by Django 4.1.4 on 2023-02-14 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_alter_saleobject_brand_name_alter_saleobject_nm_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleobject',
            name='sa_name',
            field=models.CharField(max_length=65, null=True, verbose_name='Артикул поставщика'),
        ),
        migrations.AlterField(
            model_name='saleobject',
            name='ts_name',
            field=models.CharField(max_length=65, null=True, verbose_name='Размер'),
        ),
    ]
