# Generated by Django 4.1.4 on 2023-03-16 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_rename_customeremail_order_customer_email_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order',
        ),
    ]
