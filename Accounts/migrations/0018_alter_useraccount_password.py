# Generated by Django 4.0.2 on 2022-02-27 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0017_remove_notification_end_reque_call_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='password',
            field=models.CharField(max_length=255),
        ),
    ]
