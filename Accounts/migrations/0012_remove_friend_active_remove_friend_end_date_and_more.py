# Generated by Django 4.0 on 2022-01-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0011_alter_useraccount_account_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friend',
            name='active',
        ),
        migrations.RemoveField(
            model_name='friend',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='friend',
            name='start_date',
        ),
        migrations.AddField(
            model_name='friend',
            name='state',
            field=models.CharField(choices=[('accepted', 'accepted'), ('rejected', 'rejected'), ('pending', 'pending')], default='pending', max_length=30),
        ),
    ]