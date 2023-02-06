# Generated by Django 4.1.4 on 2023-01-24 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_netcost_amount_alter_wbapikey_api_key'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='netcost',
            index=models.Index(fields=['-cost_date'], name='users_netco_cost_da_c63b7f_idx'),
        ),
    ]
