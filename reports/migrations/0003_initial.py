# Generated by Django 4.1.4 on 2023-02-17 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '0002_delete_reportbyproducttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralInformationObj',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info_type', models.CharField(blank=True, choices=[('reports_info', 'Reports')], max_length=25, null=True)),
                ('info_message', models.CharField(blank=True, max_length=625, null=True)),
            ],
        ),
    ]
