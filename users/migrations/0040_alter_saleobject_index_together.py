# Generated by Django 4.1.4 on 2023-03-18 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_remove_saleobject_product'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='saleobject',
            index_together={('api_key', 'owner')},
        ),
    ]
