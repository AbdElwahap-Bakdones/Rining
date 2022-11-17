# Generated by Django 4.0 on 2022-02-18 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0016_notification_end_reque_call_notification_name_sender_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='end_Reque_Call',
        ),
        migrations.AddField(
            model_name='notification',
            name='connection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Accounts.connection'),
        ),
    ]