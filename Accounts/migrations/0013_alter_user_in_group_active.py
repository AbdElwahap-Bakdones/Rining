# Generated by Django 4.0 on 2022-01-18 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0012_remove_friend_active_remove_friend_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_in_group',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
