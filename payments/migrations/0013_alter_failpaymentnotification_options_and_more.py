# Generated by Django 4.1.4 on 2023-03-17 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_failpaymentnotification_successpaymentnotification_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='failpaymentnotification',
            options={'verbose_name': 'Уведомление об отменённом платеже', 'verbose_name_plural': 'Уведомления об отменённых платежах'},
        ),
        migrations.AlterModelOptions(
            name='successpaymentnotification',
            options={'verbose_name': 'Уведомление об успешном платеже', 'verbose_name_plural': 'Уведомления об успешных платежах'},
        ),
        migrations.AlterField(
            model_name='subscriptiontype',
            name='duration_desc',
            field=models.CharField(choices=[('Недели', (('неделя', 'Неделя'), ('недели', 'Недели'), ('недель', 'Недель'))), ('Месяца', (('месяц', 'Месяц'), ('месяца', 'Месяца'), ('месяцев', 'Месяцев')))], max_length=10, verbose_name='Строковое описание длительности (месяц, год)'),
        ),
    ]
