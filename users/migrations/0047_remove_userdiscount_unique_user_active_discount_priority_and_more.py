# Generated by Django 4.1.4 on 2023-03-23 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_alter_order_options_alter_order_status'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='userdiscount',
            name='unique_user_active_discount_priority',
        ),
        migrations.RemoveConstraint(
            model_name='usersubscription',
            name='unique_user_active_subscription_priority',
        ),
        migrations.AddConstraint(
            model_name='userdiscount',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('is_active', 'user'), name='unique_user_active_discount_priority'),
        ),
        migrations.AddConstraint(
            model_name='usersubscription',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('is_active', 'user'), name='unique_user_active_subscription_priority'),
        ),
    ]
