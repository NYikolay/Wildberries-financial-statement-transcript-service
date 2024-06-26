# Generated by Django 4.1.4 on 2023-03-14 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payments', '0002_delete_rateobj'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third')], max_length=10, verbose_name='Тип подписки')),
                ('duration', models.IntegerField(verbose_name='Длительность подписки')),
                ('duration_desc', models.CharField(max_length=10, verbose_name='Строковое описание длительности (месяц, год)')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Стоимость подписки')),
                ('cost_for_week', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Стоимость подписки в неделю')),
                ('build_in_discount', models.IntegerField(verbose_name='Заложенная в тариф скидка')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ['cost'],
            },
        ),
        migrations.CreateModel(
            name='SuccessNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('InvId', models.IntegerField(db_index=True, verbose_name='Номер заказа')),
                ('OutSum', models.CharField(max_length=15, verbose_name='Сумма')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время получения уведомления')),
            ],
            options={
                'verbose_name': 'Уведомление об успешном платеже',
                'verbose_name_plural': 'Уведомления об успешных платежах (ROBOKASSA)',
            },
        ),
    ]
